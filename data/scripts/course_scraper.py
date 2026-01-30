import json
import requests
from bs4 import BeautifulSoup

from course_obj import Course, get_dict
from identifiers import TOI_IDS, CA_IDS, SEMESTERS_TO_COURSES
        
# --- #

url = "https://catalog.uconn.edu/undergraduate/courses/ling"
page = requests.get(url)
content = page.text
html = BeautifulSoup(content, "lxml")

courses = []

content_area = html.find_all('div', class_='courseblock')

for course_block in content_area:

    cols = course_block.find_all('div', class_='cols noindent')

    if cols[0]: # only one cols no indent block => the line with course code details, title, etc.
        number_unformatted = cols[0].find('span', class_="text detail-code margin--tiny text--semibold text--big")
        name = number_unformatted.find('strong').get_text(strip=True).strip(".")

        title_unformatted = cols[0].find('span', class_="text detail-title margin--tiny text--semibold text--big")
        title = title_unformatted.find('strong').getText.strip(".")

        # note: credit count can be variable (ex. 1-3 credits) - code in lower & upper bounds
        credit_count_unformatted = cols[0].find('span', class_="text detail-hours_html margin--tiny text--semibold text--big")
        credit_count = credit_count_unformatted.find('strong').get_text(strip=True).lstrip("(").rstrip(" Credits)").rstrip(" Credit)")

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
                # fixme: add gui for manually setting requirements
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