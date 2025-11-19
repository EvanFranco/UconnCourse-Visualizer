class Course:
    
    def __init__(self, name, dept_code, id_number, title, credits):
        self.name = name
        self.dept_code = dept_code
        self.id_number = id_number
        self.title = title
        
        self.description = ""
        self.credits = credits
        self.requirement_description = "No requirements to take this course."
        self.restrictions = {}
        self.content_areas = []
        self.tois = []
        self.skill_codes = []
        self.lab = False
        
        # add these to spec doc!
        self.honors_credit = False
        self.max_credit_repeats = 0 # None (null) if no limit exists, 0 if none allowed, # if there is a specified limit
    
    def print_restriction_desc(self):
        print(f"Restriction description: {self.requirement_description}\n")

def get_dict(obj):
    return obj.__dict__