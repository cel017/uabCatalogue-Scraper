from course import *

import re
import json
import requests
from pathlib import Path
from typing import Generator
from bs4 import BeautifulSoup, SoupStrainer

LINKS_PATH = Path(__file__).parents[1]/"data"/"links.json"
assert LINKS_PATH.exists(), "links.json not found"
with open(LINKS_PATH) as f:
    LINKS = json.load(f)

def scrape_subjects():
    '''generator function to scrape subjects
        
    yields:
        (tuple): subj_code: subj_name
    '''

    subj_hrefs = BeautifulSoup(
        markup=requests.get(LINKS["subjects"]).text,
        features="lxml",
        parse_only=SoupStrainer(href=re.compile(r"^\/catalogue\/course\/"))).find_all()

    for elem in subj_hrefs:
        # [:18] <- 'course/catalogue/'
        yield (elem.get("href")[18:], elem.text)

def scrape_courses(subjects: tuple):
    '''generator function to scrape basic course info

    args:
        subjects: tuple of subjects (subj_code, subj_name)

    yields:
        (tuple): course info (course_code, course_name, course_descr)
    '''

    for subj_code, _ in subjects:
        # strain cards ignoring future courses; get href to course page
        course_cards = BeautifulSoup(
            markup=requests.get(f"{LINKS['subjects']}/{subj_code}").text,
            features="lxml",
            parse_only=SoupStrainer(class_="course first")).find_all(href=True)

        i = 0
        while i < len(course_cards):
            course = course_cards[i]
            course_page=course.get("href")
            # skip next iter if same href as current
            # (link on 'view class' btn)
            if i+1 != len(course_cards) and course_page == course_cards[i+1].get("href"): 
                i += 1
            else:
                # TODO <- have a flag to scrape
                # deets in this page without going deeper
                i+=1
                continue
            # retrieve deets
            course_code = course_page[18:]
            course_name = course.text
            course_creds_tag =course.find_next("b")
            # 'b' tag has creds, followed by 'p' usually (description)
            course_descr_tag = course_creds_tag.find_next()
            if course_descr_tag.name=="p":
                course_descr=course_descr_tag.text
            else:
                # no descr => div clas="alert..."
                course_descr=""
            
            i+=1
            yield Course(course_code, course_name, course_descr)
            
def scrape_sections(course_code): 
    '''get courses with their scraped sections
    
    args:
        courses: list of Course objects
        start: index to start scraping
        
    returns:
        Course: sequence of Course objects with scraped sections
    '''

    section_list = []
    table_elems = BeautifulSoup(
        markup=requests.get(f"{LINKS['subjects']}/{course_code}").text,
        features="lxml",
        parse_only=SoupStrainer(class_="mb-5")).find_all("table")
    
    # TODO <- retrieve data-card-titles without assuming order
    for table in table_elems:
        if not table.find_previous_sibling(): continue
        section_type = table.find_previous_sibling().text[:3]
        table_data_tags = table.findChildren(attrs={"data-card-title": True})
        row_cnt = len(table_data_tags)//4  # cols = 4
        for row in range(row_cnt):
            # get data and clean whitespace/newline chars  
            row_data = tuple(' '.join(table_data_tags[4*row+i].contents[1].text.split()) for i in range(4))
            section_list.append(Section(section_type, *row_data))

    return section_list

def get_finals_data():
    # gets the json file for finals schedule 

    # TODO <- if the request for finals_data is invalid, scrape the updated call from 
    # 'https://www.ualberta.ca/registrar/examinations/exam-schedules/fall-winter-exam-schedule.html'
    return requests.get(LINKS['finals']).json()["data"]
