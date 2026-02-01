import json
import os

import requests
from bs4 import BeautifulSoup

from course_obj import Course, get_dict
from identifiers import TOI_IDS, CA_IDS, SEMESTERS_TO_COURSES
        
# --- #

BASE_URL = "https://catalog.uconn.edu/undergraduate/courses/"
BASE_GRAD_URL = "https://catalog.uconn.edu/graduate/courses/"
root_directory = "C:\\[FlowScholar]\\UconnCourse-Visualizer\\data\\courses"
recursive_depth = 0

def generate_courses(subject_code: str, graduate_courses: bool):

    print("Making dir...")

    os.makedirs(f"{root_directory}\\{subject_code.upper()}", exist_ok=True)

    if graduate_courses:
        url = BASE_GRAD_URL + subject_code.lower() + "/"
    else:
        url = BASE_URL + subject_code.lower() + "/"

    print(f"Getting page {url}")
    try:
        page = requests.get(url)
    except:
        print(f"HTML request for {url} failed. Trying again...")
        generate_courses(subject_code) # in case html get fails, try again (usually works)
        return

    content = page.text
    html = BeautifulSoup(content, "lxml")
    content_area = html.find_all('div', class_='courseblock')

    for course_block in content_area:

        course_sections = course_block.find_all('div', class_='noindent')

        name = course_sections[0].find('span', class_="text detail-code margin--tiny text--semibold text--big").get_text(strip=True).strip(".")

        title = course_sections[0].find('span', class_="text detail-title margin--tiny text--semibold text--big").get_text(strip=True).strip(".")

        # note: credit count can be variable (ex. 1-3 credits) - code in lower & upper bounds
        credit_count = course_sections[0].find('span', class_="text detail-hours_html margin--tiny text--semibold text--big").get_text(strip=True).lstrip("(").rstrip(" Credits)").rstrip(" Credit)")

        split_name = name.split()

        current_course = Course(name, split_name[0], split_name[1], title, credit_count)

        description_zone = course_sections[1].find('div', class_='courseblockextra noindent')

        if description_zone:
            current_course.description = description_zone.get_text() # split and join removes weird \u character for spaces

        for course_info in range(3, len(course_sections)):
            content = course_sections[course_info]

            text = content.get_text().strip()
            if not text: # lots of blank divs here for no reason lol
                continue

            category = text.split(":", 1) # splits "<IDENTIFIER>:"" from information

            clause_identifier = category[0]
            if len(category) > 1:
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

                case "Grading Basis":
                    if "Honors Credit" in data_description:
                        current_course.honors_credit = True

                case _:
                    print(f"The code category {clause_identifier} has not been accounted for.")
                    # apply credit repeats

        course_file = open(f"{root_directory}\\{subject_code}\\{current_course.name}.json", "w")
        json.dump(current_course, course_file, default=get_dict, indent=4)

print("WARNING: SET UP THE OUTPUT DIRECTORY IN MAIN FUNC BEFORE RUNNING! DIRECTORY IS HARDCODED")
print("UCONN course scraper. Scrape individual page (I) or batch scrape all known courses (B)?")
choice = input("\t ")
graduate_yn = input("Do graduate courses instead of undergrad? (y/n): \n\t")
graduate_courses = graduate_yn == "y" or graduate_yn == "Y"

if choice == "I":
    code = input("Enter 2-4 letter code corresponding to the webpage needed.")
    generate_courses(code, graduate_courses)
else:
    if graduate_courses:
        course_reference = "known_graduate_course_codes.txt"
    else:
        course_reference = "known_course_codes.txt"

    with open(course_reference, "r") as known_course_text:
        for i in known_course_text:
            print(f"Scanning {i}")
            generate_courses(i.strip(), graduate_courses)
