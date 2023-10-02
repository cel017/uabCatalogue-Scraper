from database_writer import DatabaseWriter
from scraper import *

from time import perf_counter
from pathlib import Path


if __name__ == "__main__":
    db_writer = DatabaseWriter(Path(__file__).parents[1]/"data/catalogue.db")
    db_writer.create_tables()
    
    st = perf_counter()
    # write Subjects
    subjects = tuple(scrape_subjects())
    db_writer.write_subjects(subjects)
    print(perf_counter()-st)
    
    st = perf_counter()
    # iterate through courses and populate
    # with components (lec/lab/sem)
    for course in scrape_courses(subjects):
        # <parse descr> #
        # lec, lab, sem = scrape_sections(course.code)
        # <parse components> #
        db_writer.write_course(course)

    print(perf_counter()-st)
    db_writer.close_db()