class Course:
    def __init__(self, code: str, name: str, descr: str, lecs: list, labs: list, seminars: list):
        self.code = code
        self.name = name
        self.descr = descr
        self.lecs = lecs
        self.labs = labs
        self.seminars = seminars

    def __iter__(self):
        for k, v in self.__dict__.items():
            if k in ("lecs", "labs", "seminars"):
                yield k, [c.__dict__ for c in v]
            else:
                yield k, v
    
    def parse_descr(self):
        pass

class Component:
    def __init__(self, section, capacity, duration, instructors):
        self.section = section
        self.capacity = capacity
        self.duration = duration  
        self.instructors = instructors
    
    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v

    def set_finals(self):
        pass

    def parse_duration(self):
        pass
