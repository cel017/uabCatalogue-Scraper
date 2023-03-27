class Course:
    def __init__(self, code: str, name: str, descr: str, lecs = [], labs = [], seminars = []):
        self.code = code
        self.name = name
        self.descr = descr
        self.lecs = lecs
        self.labs = labs
        self.seminars = seminars
    
    def __repr__(self):
        cmb = lambda X: ''.join(map(str, X))
        return f"{self.name}\n\n{self.descr}\n\nLectures:\
            \n{cmb(self.lecs)}\nLabs:\n{cmb(self.labs)}\nSeminars:\n{cmb(self.seminars)}"

    def to_dict(self):
        return {"code": self.code, "name": self.name, "descr": self.descr, \
                "lecs": [i.__dict__ for i in self.lecs], \
                "labs": [i.__dict__ for i in self.labs], \
                "seminars": [i.__dict__ for i in self.seminars]}

    def parse_descr(self):
        pass

class Component:
    def __init__(self, section, capacity, duration, instructors):
        self.section = section
        self.capacity = capacity
        self.duration = duration  
        self.instructors = instructors

        self.finals = None
    
    def __repr__(self):
        return "\t|\t".join(self.__dict__.values())+"\n"
    
    def set_finals(self):
        pass

    def parse_duration(self):
        pass

