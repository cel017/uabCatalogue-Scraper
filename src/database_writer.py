from course import *

import sqlite3
from pathlib import Path

class DatabaseWriter:
    def __init__(self, path: Path) -> None:
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close_db(self):
        if not self.conn: return
        self.conn.commit()
        self.conn.close()

    def create_tables(self):
        # Subjects
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Subjects (
            subject_code TEXT PRIMARY KEY,
            subject_name TEXT
        )''')

        # Courses
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Courses (
                            subject_code TEXT,
                            course_number TEXT,
                            course_name TEXT,
                            course_description TEXT,
                            PRIMARY KEY (subject_code, course_number),
                            FOREIGN KEY (subject_code) REFERENCES Subjects (subject_code)
                            )''')

        # sections
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Sections (
                            section_type TEXT,
                            course_code TEXT,
                            section TEXT,
                            capacity INT,
                            instructors TEXT, 
                            duration TEXT,
                            PRIMARY KEY (course_code, section)
                            )''')

        self.conn.commit()

    def write_subjects(self, subjects: list):
        self.cursor.executemany("INSERT INTO Subjects VALUES (?, ?)",
                                subjects)
        self.conn.commit()
    
    def write_course(self, course: Course):
        query = f'''INSERT INTO Courses 
                    (subject_code, course_number, course_name, course_description) 
                    VALUES (?, ?, ?, ?)'''
        self.cursor.execute(query, (course.subj, course.number, course.name, course.descr))
        self.conn.commit()
    
    def write_sections(self, sections_list: list, course: Course):
        query = f'''INSERT INTO Sections 
                    (section_type, course_code, section, capacity, duration, instructors) 
                    VALUES (?, ?, ?, ?, ?, ?)'''
        self.cursor.executemany(query, 
                                [*((c.section_type, course.code , c.section, c.capacity, c.duration, c.instructors)
                                    for c in sections_list)])
        self.conn.commit()