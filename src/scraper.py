from course import *

import re
import json
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer


# CONSTANTS
REQUIRED_FILES = ("links.json",)

# FUNCTIONS
def get_data():
    # TODO <- command line args for required data
    data_dir = Path(__file__).parents[1]/"data"
    dpath = {}
    for path in data_dir.iterdir():
        if path.is_file(): dpath[path.name] = path

    for f in REQUIRED_FILES:
        assert f in dpath, f"{f} file missing from data directory"
        
    # read links from links.json file
    with open(dpath["links.json"]) as f:
        links = json.load(f)
    
    # scrape sections
    if "subjects.json" not in dpath:
        print("Scraping Subjects...")
        subjects = scrape_subjects(links["subjects"])
        with open(data_dir/"subjects.json", "w") as f:
            json.dump(subjects, f, indent=4)
    else:
        print("Loading Subjects From Local File...")
        with open(dpath["subjects.json"]) as f:
            subjects = json.load(f)

    print(f"({len(subjects)}) Subjects Scraped.\n")
    
    # scrape courses    
    if "courses.json" not in dpath:
        print("Scraping Courses...")
        courses = scrape_courses(links["subjects"], subjects.keys())
        dpath["courses.json"] = data_dir/"courses.json"
        with open(dpath["courses.json"], "w") as f:
            json.dump({"secs_scraped": False, "data": [dict(crs) for crs in courses]}, f, indent=4)
        secs_scraped = False
    else:
        with open(dpath["courses.json"]) as f:
            print("Loading Courses From Local File...")
            courses_json = json.load(f)
        secs_scraped = courses_json["secs_scraped"]
        # assumes order is preserved (py3.7> dict) ->
        # might cause attr order issues if file is manipulated elsewhere
        courses = []
        for crs in courses_json["data"]:
            init_args = list(crs.values())
            # builtin dtypes
            std_args = init_args[:3]
            # component args as list of dicts of attrs
            comp_args_raw = init_args[3:]
            # get list of objects for list of dict from json
            comp_args = []
            for comp_list in comp_args_raw:
                comp_args.append([Component(*c.values()) for c in comp_list])
            all_args = std_args+comp_args
            courses.append(Course(*all_args))
    print(f"({len(courses)}) Courses Scraped.")
    
    # scrape sections
    if not secs_scraped:
        # TODO <- Refactor to use a generator func for scrape sections;
        # save time on already scraped data in case of crashes
        print("\nScraping Sections...")
        scrape_sections(links["subjects"], courses)
        dpath["courses.json"].unlink(missing_ok=False)
        with open(dpath["courses.json"],  "w") as f:
            json.dump({"secs_scraped": True, "data": [dict(crs) for crs in courses]}, f, indent=4)
        print("All Sections Scraped.")
    else:
        print("Sections Found in Local File.")

    return courses

def scrape_subjects(url: str) -> dict[str: str]:
    '''gets a dict of all offered subject names with code keys
    
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
    '''gets a list of Course objects

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

        i = 0
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
            courses.append(Course(crs_code, crs_name, crs_descr, [], [], []))
            i+=1

    return courses

def scrape_sections(url: str, courses: list):
    for crs in courses:
        table_elems = BeautifulSoup(requests.get(f"{url}/{crs.code}").text, "lxml", \
        parse_only=SoupStrainer(class_="card-body")).find_all("table")
        for table in table_elems:
            # lecture/lab/seminar
            component_type = table.find_previous_sibling().text
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
                case _:
                    raise ValueError

def get_finals_data(url: str):
    # gets the json file for finals schedule 

    # TODO <- if the request for finals_data is invalid, scrape the updated call from 
    # 'https://www.ualberta.ca/registrar/examinations/exam-schedules/fall-winter-exam-schedule.html'
    return requests.get(url).json()["data"]

def clear(backup):
    data_dir = Path(__file__).parents[1]/"data"
    if backup:
        backup_dir = data_dir/"backup"/f"{datetime.now().strftime('%Y_%m_%d')}"
        backup_dir.mkdir(parents=True)
    for path in data_dir.iterdir():
        if path.name == "links.json" or path.is_dir():
            continue
        if backup:
            dest = backup_dir/path.name
            dest.write_text(path.read_text())
        path.unlink()

if __name__ == "__main__":
    clear(backup = True)
    get_data()
