import json
import requests
from bs4 import BeautifulSoup

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
        

url = "https://catalog.uconn.edu/undergraduate/courses/ling"
page = requests.get(url)
content = page.text
html = BeautifulSoup(content, "lxml")

TOI_IDS = ("TOI1", "TOI2", "TOI3", "TOI4", "TOI5", "TOI6", "TOI6L")
CA_IDS = ("CA1", "CA2", "CA3", "CA3LAB", "CA4", "CA4INT")

# https://policy.uconn.edu/2011/06/02/undergraduate-earned-credits-semester-standing/ 
SEMESTERS_TO_COURSES = {
    1: 11,
    2: 23,
    3: 39,
    4: 53,
    5: 69, # nice
    6: 85,
    7: 99,
    8: 116,
    9: 133,
    10: None
}

courses = []

content_area = html.find_all('div', class_='courseblock')

def get_dict(obj):
    return obj.__dict__

def get_courses():
    courses = input("Enter course IDs, separated by &&. Enter course OR with \"||\" \n\t")
    split_courses = courses.split("&&") 

    course_arr = []

    for i in split_courses:
        course = i.strip()
        options_arr = []
        if ("||" in course):
            options = course.split("||")

            for i in options:
                option = i.strip()
                options_arr.append(option)

        else:
            options_arr.append(course)

        course_arr.append(options_arr)
    return course_arr

def manual_set_requirements(current_course: Course):
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print(f"\nAction needed for course {current_course.name}")
    print(f"Restriction description: {current_course.requirement_description}\n")
    
    options_str = """
    Select option to continue, or enter -1 to flag this course for a restriction review.
    Enter "f" to exit restriction builder.
    Enter the number to enter a new set of courses that fill that requirement, or enter "0" for no more restrictions.
    1: prereq
    2: concurrency
    3: coreq
    4: block
    5: credit range
    6: recommendation
    7: major restriction
    8: school restriction
    """
    print(options_str)
    restriction_type = input()

    while(restriction_type != "f"):
        match int(restriction_type):
            case -1:
                current_course.restrictions["needs review"] = True
                # also add to a list of courses to edit later
            case 0:
                break
            case 1:
                current_course.restrictions["prereq"] = get_courses()
            case 2:
                current_course.restrictions["concurrency"] = get_courses()
            case 3:
                current_course.restrictions["coreq"] = get_courses()
            case 4:
                current_course.restrictions["block"] = get_courses()
            case 6:
                current_course.restrictions["recommendation"] = get_courses()
            case 5:
                # add this to spec doc: range of credits is sometimes needed
                limit = input("Enter credit range, separated by commas, or enter semester range, separated by \"-\" \n\t")
                comma_sep = limit.split(",")

                range = []
                if len(comma_sep) == 2:
                    range.append(int(comma_sep[0].strip()))
                    range.append(int(comma_sep[1].strip()))

                dash_sep = limit.split("-")
                if len(dash_sep) == 2:
                    range.append(SEMESTERS_TO_COURSES[int(dash_sep[0].strip())])
                    range.append(SEMESTERS_TO_COURSES[int(dash_sep[1].strip())])
                
                current_course.restrictions["credit_range"] = (range[0], range[1])
            case 7:
                majs_in = input("Enter majors, separated by commas. If minor, add (minor) after the program name.\n\t")

                majs = majs_in.split(",")

                majs_arr = []

                for i in majs:
                    majs_arr.append(i.strip())
                
                current_course.restrictions["only_major"] = majs_arr
            case 8:
                schools_in = input("Enter schools, separated by commas.\n\t")

                schools = schools_in.split(",")

                schools_arr = []
                
                for i in schools:
                    schools_arr.append(i.split())
                
                current_course.restrictions["school"] = schools_arr
        

        print("--------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"{current_course.name} Current restrictions: \n{json.dumps(current_course.restrictions, indent=4)}\n")
        cont = input(f"Restriction description: {current_course.requirement_description} \nMore restrictions? Y/N\n\t")
        if (cont == "N"):
            break


        print(options_str)
        restriction_type = input()
        # print current restrictions added

def get_sections(desc: str):
    semicolon_split = desc.split(";")
    all_zones = []

    for zone in semicolon_split:
        if "." in zone:
            period_split = zone.split(".")
            all_zones.append(period_split)
            continue
        all_zones.append(zone)
    
    return all_zones

def detect_requirements(current_course: Course):
    desc = [current_course.requirement_description]

    sections = get_sections(desc)

    # if no code in number, inherit last detected code
    # detect or
    # detect Recommended preparation:
    # detect Not open to students
    # detect Not open for credit 


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
        current_course.description = ' '.join(description_zone.getText(strip=True).split()) # split and join removes weird \u character for spaces

    for course_info in range(len(noindent)):
        if (course_info < 3): # avoid descriptions
            continue

        content = noindent[course_info]

        text = content.get_text().strip()
        if (not text): # lots of blank divs here for no reason lol
            continue

        category = text.split(":", 1) # splits "<IDENTIFIER>:"" from information

        clause_identifier = category[0]
        if (len(category) > 1):
            data_description = category[1]

        match clause_identifier:
            case "Enrollment Requirements":
                current_course.requirement_description = ' '.join(data_description.strip().split()) # split and join removes weird \u character for spaces
                # automatically detect some common formats here (detect_requirements())
                manual_set_requirements(current_course)
                # todo: add json editor (meaning, open up existing scraped data, and edit the restrictions/other categories that way)
            
            case "Skill Codes":
                codes = []
 
                if "Quantitative" in data_description:
                    codes.append("Q")
                if "Writing" in data_description:
                    codes.append("W")
                if "Environmental" in data_description:
                    codes.append("E")

                current_course.skill_codes = codes

            case "Topics of Inquiry":
                this_tois = []
                lab = False

                for toi in TOI_IDS:
                    if toi in data_description:
                        this_tois.append(toi)
                        if "L" in toi:
                            lab = True
                
                current_course.tois = this_tois
                current_course.lab = lab

            case "Content Areas":
                this_cas = []
                lab = False

                for area in CA_IDS:
                    if area in data_description:
                        this_cas.append(area)
                        if "LAB" in area:
                            lab = True
                
                current_course.content_areas = this_cas
                current_course.lab = lab

            case s if "May be repeated" in clause_identifier:
                # Add extra case in spec doc for repetition guidelines
                # Add field in object for credit maximum
                current_course.description = current_course.description + " " + clause_identifier + "."
                if "May be repeated" in clause_identifier:
                    current_course.max_credit_repeats = None
                if "May be repeated for a total of" in clause_identifier:
                    current_course.max_credit_repeats = [int(char) for char in clause_identifier if char.isdigit()][0]
                    print(current_course.max_credit_repeats)
            
            case "Grading Basis":
                if "Honors Credit" in data_description:
                    current_course.honors_credit = True
            
            case _:
                print(f"The code category {clause_identifier} has not been accounted for.")
                # apply credit repeats

    course_file = open(f"C:\\[FlowScholar]\\UconnCourse-Visualizer\\data\\courses\\{current_course.name}.json", "w")
    json.dump(current_course, course_file, default=get_dict, indent=4)
    courses.append(current_course)