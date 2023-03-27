import re
import json
import requests
from course import *
from pathlib import Path
from bs4 import BeautifulSoup, SoupStrainer

# TODO -> command line args for required data
def scrape_all():
    data_dir = Path(__file__).parents[1]/"data"
    dpath = {}
    for path in data_dir.iterdir():
        dpath[path.name] = path

    for f in ("links.json",):
        assert f in dpath, f"{f} file missing from data directory"
    # read links from links.json file
    with open(dpath["links.json"]) as f:
        links = json.load(f)
    
    # scrape sections
    if "subjects.json" in dpath:
        print("Scraping Subjects...")
        subjects = scrape_subjects(links["subjects"])
        with open(data_dir/"subjects.json", "w") as f:
            json.dump(subjects, f, indent=4)
    else:
        print("Loading Subjects From Local File...")
        with open(dpath["subjects.json"]) as f:
            subjects = json.load(f)

    print(f"({len(subjects)}) Subjects Found.\n")
    
    # scrape courses    
    secs_scraped = False   
    if "courses.json" not in dpath:
        print("Scraping Courses...")
        courses = scrape_courses(links["subjects"], subjects.keys())
        with open(data_dir/"courses.json", "w") as f:
            json.dump({"secs_scraped": False, "data": [crs.__dict__ for crs in courses]}, f, indent=4)
    else:
        with open(dpath["courses.json"]) as f:
            print("Loading Courses From Local File...")
            courses_json = json.load(f)
        secs_scraped = courses_json["secs_scraped"]
        # assumes order is preserved (py3.7> dict) ->
        # attr order issues if file is manipulated by a script
        if not secs_scraped:
            courses = [Course(*crs.values()) for crs in courses_json["data"]]
        else:
            courses = []
            for crs in courses_json["data"]:
                init_args = list(crs.values())
                # builtin dtypes
                std_args = init_args[:3]
                comp_args_raw = [c for c in init_args[3:]]
                # get list of objects for list of dict from json
                comp_args = []
                for comp_list in comp_args_raw:
                    comp_args.append([Component(*c.values()) for c in comp_list])
                all_args = std_args+comp_args
                courses.append(Course(*all_args))
    print(f"({len(courses)}) Courses Found.\n")
    
    # scrape sections
    if not secs_scraped:
        print("Scraping Sections...")
        scrape_sections(links["subjects"], courses)
        with open(data_dir/"courses.json", "w") as f:
            json.dump({"secs_scraped": True, "data": [crs.to_dict() for crs in courses]}, f, indent=4)
        print("All Sections Found.")
    else:
        print("Sections Found in Local File.")

    # scrape finals
    finals = get_finals_data(links["finals"])


def scrape_subjects(url: str) -> dict[str: str]:
    '''get a dict of all offered subject names with code keys
    
    args:
        url(str): url to subject catalogue
        
    returns:
        (dict[str: str]): [subj_code: subj_name]
    '''

    subj_hrefs = BeautifulSoup(requests.get(url).text, "lxml", \
    parse_only=SoupStrainer(href=re.compile(r"^\/catalogue\/course\/"))).find_all()
    # remove [:18] 'course/catalogue/'
    subjects = {elem.get("href")[18:] : elem.text for elem in subj_hrefs}
    return subjects

def scrape_courses(url: str, subjects: list) -> list[Course]:
    '''get a list of Course objects

    args:
        url(str): url to subject catalogue
        subjects(dict): list of subject codes

    returns:
        (list[Course])
    '''
    courses = []
    for subj_code in subjects:
        # strain cards ignoring future courses; get href to course page
        crs_cards = BeautifulSoup(requests.get(f"{url}/{subj_code}").text, "lxml", \
        parse_only=SoupStrainer(class_="course first")).find_all(href=True)

        i=0
        while i < len(crs_cards):
            crs = crs_cards[i]
            crs_page=crs.get("href")
            # skip next iter if same href as current
            # (link on 'view class' btn)
            if i+1!=len(crs_cards) and crs_page == crs_cards[i+1].get("href"): 
                i+=1
            else:
                # TODO <- have a flag to scrape
                # deets in this page without going deeper
                i+=1
                continue
            # retrieve deets
            crs_code = crs_page[18:]
            crs_name = crs.text
            crs_creds_tag =crs.find_next("b")
            # 'b' tag has creds, followed by 'p' usually (description)
            crs_descr_tag = crs_creds_tag.find_next()
            if crs_descr_tag.name=="p":
                crs_descr=crs_descr_tag.text
            else:
                # no descr => div clas="alert..."
                crs_descr=""
            
            courses.append(Course(crs_code, crs_name, crs_descr))
            i+=1

    return courses

def scrape_sections(url: str, courses: list):
    for crs in (courses):
        table_elems = BeautifulSoup(requests.get(f"{url}/{crs.code}").text, "lxml", \
        parse_only=SoupStrainer(class_="card-body")).find_all("table")

        for table in table_elems:
            component_type = table.find_previous_sibling().text  # lecture/lab/seminar
            table_data_tags = table.findChildren(attrs={"data-card-title": True})

            comp_list = []
            row_cnt = len(table_data_tags)//4  # cols = 4
            for row in range(row_cnt):
                # get data and clean whitespace/newline chars  
                row_data = tuple(' '.join(table_data_tags[4*row+i].contents[1].text.split()) for i in range(4))
                comp_list.append(Component(*row_data))
            match component_type:
                case "Lectures":
                    crs.lecs.extend(comp_list)
                case "Labs":
                    crs.labs.extend(comp_list)
                case "Seminars":
                    crs.seminars.extend(comp_list)
    return

def get_finals_data(url: str):
    # get the json file for finals schedule 

    # TODO <- if the request for finals_data is invalid, scrape the updated call from 
    # 'https://www.ualberta.ca/registrar/examinations/exam-schedules/fall-winter-exam-schedule.html'
    return requests.get(url).json()["data"]

if __name__ == "__main__":
    scrape_all()