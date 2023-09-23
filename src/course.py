class Course:
    def __init__(self, code: str, name: str, descr: str, lecs: list, labs: list, seminars: list):
        self.code = code
        self.name = name
        self.descr = descr
        self.lecs = lecs
        self.labs = labs
        self.seminars = seminars

    def parse_descr(self):
        pass

class Component:
    def __init__(self, section, capacity, duration, instructors):
        self.section = section
        self.capacity = capacity
        self.duration = duration  
        self.instructors = instructors
    
    def set_finals(self):
        pass

    def parse_duration(self):
        pass

