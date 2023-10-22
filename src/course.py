class Course:
    def __init__(self, code: str, name: str, descr: str):
        self.code = code
        self.subj, self.number = code.split('/')
        self.name = name
        self.descr = descr

    def __iter__(self):
        for k, v in self.__dict__.items():
            if k in ("lecs", "labs", "seminars"):
                yield k, [c.__dict__ for c in v]
            else:
                yield k, v
    
    def parse_descr(self):
        # parse to get prereqs/coreqs
        pass

class Section:
    def __init__(self, section_type, section, capacity, duration, instructors):
        self.section_type = section_type
        self.section = section
        self.capacity = capacity
        self.duration = duration  
        self.instructors = instructors
    
    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v

    def parse_duration(self):
        pass
