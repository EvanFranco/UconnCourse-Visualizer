import json
import os

counter = 0

# Currently filtered easy requirements:
# Single courses (ex. "CSE 1010." or "CSE 2050")

def detect_a_course(course_str: str):

    course_str = course_str.strip().strip(";").strip(".")

    course_parts = course_str.split(" ")

    if len(course_parts) != 2:
        #print(f"Not a course: {course_str}. Not correct length.")
        return None

    if not(2 <= len(course_parts[0]) <= 4 and course_parts[0].isupper()):
        #print(f"Not a course: {course_str}. Dept is not valid.")
        return None

    if not(3 <= len(course_parts[1]) <= 4 and course_parts[1].isnumeric()):
        #print(f"Not a course: {course_str}. Code is not numeric.")
        return None

    return f"{course_parts[0]} {course_parts[1]}"


def detect_all_courses(req_string: str, title):

    """
        if " or " in req_string:
            courses = req_string.split(" or ")

            for i in courses:
                print(f"Is a course: {detect_a_course(i)}")

        if " and " in req_string:
            courses = req_string.split(" and ")

            for i in courses:
                print(f"Is a course: {detect_a_course(i)}")
    """

    string = detect_a_course(req_string)

    if string is not None:
        global counter
        counter += 1

        return [[string]]

    return None



with open("not_completed_courses.json", "r") as jsonfile:
    data = json.load(jsonfile)

courses_list = list(data)
output_courses_list = courses_list[:]

for i in courses_list:
    with open(i, "r", encoding='utf-8') as course:

        jsonfile = json.load(course)
        reqs = jsonfile['requirement_description']

        req = detect_all_courses(reqs, jsonfile['name'])

        if (req is not None):
            jsonfile['restrictions']["prereq"] = req

            output_courses_list.remove(i)

            with open(i, "w", encoding='utf-8') as writer:
                json.dump(jsonfile, writer, indent=4)

            print("Resolved", jsonfile['title'])

with open("not_completed_courses.json", "w") as jsonfile:
    json.dump(output_courses_list, jsonfile, indent=4)

print(f"Removed {counter} courses.")
