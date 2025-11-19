import json
import requests
from bs4 import BeautifulSoup

class Course:
    
    def __init__(self, name, dept_code, id_number, title, credits):
        self.name = name
        self.dept_code = dept_code
        self.id_number = id_number
        self.title = title
        
        self.description = "Description for this course is blank."
        self.credits = credits
        self.requirement_description = "No requirements to take this course."
        self.restrictions = {}
        self.content_areas = []
        self.tois = []
        self.skill_codes = []
        self.lab = False
        
        # add these to spec doc!
        self.honors_credit = False
        

url = "https://catalog.uconn.edu/undergraduate/courses/ling"
page = requests.get(url)
content = page.text
html = BeautifulSoup(content, "lxml")

TOI_IDS = ("TOI1", "TOI2", "TOI3", "TOI4", "TOI5", "TOI6", "TOI6L")
CA_IDS = ("CA1", "CA2", "CA3", "CA3LAB", "CA4", "CA4INT")

courses = []

content_area = html.find_all('div', class_='courseblock')
for course_block in content_area:

    cols = course_block.find_all('div', class_='cols noindent')

    if cols[0]: # only one cols no indent block => the line with course code details, title, etc.
        number_unformatted = cols[0].find('span', class_="text detail-code margin--tiny text--semibold text--big")
        name = number_unformatted.find('strong').get_text(strip=True).strip(".")

        title_unformatted = cols[0].find('span', class_="text detail-title margin--tiny text--semibold text--big")
        title = title_unformatted.find('strong').getText(strip=True).strip(".")

        # note: credit count can be variable (ex. 1-3 credits) - code in lower & upper bounds
        credit_count_unformatted = cols[0].find('span', class_="text detail-hours_html margin--tiny text--semibold text--big")
        credit_count = credit_count_unformatted.find('strong').get_text(strip=True).lstrip("(").rstrip(" Credits)").rstrip(" Credit")

        split_name = name.split()

        current_course = Course(name, split_name[0], split_name[1], title, credit_count)

    noindent = course_block.find_all('div', class_='noindent')
    description_zone = noindent[1].find('div', class_='courseblockextra noindent')
    if (description_zone):
        current_course.description = ' '.join(description_zone.getText(strip=True).split())

    for course_info in range(len(noindent)):
        if (course_info < 3): # avoid descriptions
            continue

        content = noindent[course_info]
        text = content.get_text().strip()
        if (not text):
            continue

        category = text.split(":", 1) # splits "<IDENTIFIER>:"" from information

        match category[0]:
            case "Enrollment Requirements":
                current_course.requirement_description = ' '.join(category[1].strip().split())
                
                # add code here to specify restrictions in flowchart-friendly form 
                # todo: add restriction specializer
                # todo: add json editor (meaning, open up existing scraped data, and edit the restrictions/other categories that way)
            
            case "Skill Codes":
                codes = []
                skill_code = category[1].strip()
 
                if "Quantitative" in skill_code:
                    codes.append("Q")
                if "Writing" in skill_code:
                    codes.append("W")
                if "Environmental" in skill_code:
                    codes.append("E")

                current_course.skill_codes = codes

            case "Topics of Inquiry":
                this_tois = []
                lab = False
                for toi in TOI_IDS:
                    if toi in category[1]:
                        this_tois.append(toi)
                        if "L" in toi:
                            lab = True
                
                current_course.tois = this_tois
                current_course.lab = lab

            case "Content Areas":
                this_cas = []
                lab = False
                for area in CA_IDS:
                    if area in category[1]:
                        this_cas.append(area)
                        if "LAB" in area:
                            lab = True
                
                current_course.content_areas = this_cas
                current_course.lab = lab

            case s if "May be repeated" in category[0]:
                # Add extra case in spec doc for repetition guidelines
                # Add field in object for credit maximum
                current_course.description = current_course.description + " " + category[0] + "."
            
            case "Grading Basis":
                if "Honors Credit" in category[1]:
                    current_course.honors_credit = True
            
            case _:
                print(f"The code category {category[0]} has not been accounted for.")
                # apply credit repeats

    courses.append(current_course)

def get_dict(obj):
    return obj.__dict__
    
file = open("C:\\[FlowScholar]\\UconnCourse-Visualizer\\courses.json", "w")
json.dump(courses, file, default=get_dict, indent = 4)