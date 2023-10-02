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

        # Components
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Components (
                            component_type TEXT,
                            course_code TEXT,
                            capacity, INT
                            instructor TEXT, 
                            FOREIGN KEY (course_code) REFERENCES Courses (course_code),
                            PRIMARY KEY (course_code, component_type, component_type)
                            )''')

        self.conn.commit()

    def write_subjects(self, subjects: tuple):
        self.cursor.executemany("INSERT INTO Subjects VALUES (?, ?)",
                                subjects)
        self.conn.commit()
    
    def write_course(self, course: Course):
        query = f'''INSERT INTO Courses 
                    (subject_code, course_number, course_name, course_description) 
                    VALUES (?, ?, ?, ?)'''
        self.cursor.execute(query, (course.subj, course.number, course.name, course.descr))
        self.conn.commit()