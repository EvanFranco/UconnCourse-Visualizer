import json
import os

VALID_NON_NUMERIC_CODES = ["W", "E", "Q", "WE", "WQ"]

counter = 0

# Currently filtered easy requirements:
# Single courses (ex. "CSE 1010." or "CSE 2050")
    # Note: did not catch classes with Q, W or E.
# "Department consent."
# "Instructor consent."

def detect_a_course(course_str: str):
    course_str = course_str.strip().strip(";").strip(".")

    course_parts = course_str.split(" ")

    if len(course_parts) != 2:
        # print(f"Not a course: {course_str}. Not correct length.")
        return None

    if not(2 <= len(course_parts[0]) <= 4 and course_parts[0].isupper()):
        # print(f"Not a course: {course_str}. Dept is not valid.")
        return 1

    if not(3 <= len(course_parts[1]) <= 6 or course_parts[1][0:4].isnumeric()):
        # print(f"Not a course: {course_str}. Code is not numeric.")
        return None

    return f"{course_parts[0]} {course_parts[1]}"

def detect_all_courses(jsonfile) -> bool:

    req = jsonfile['requirement_description']

    print(req)
    if req == "Open to juniors or higher.":
        jsonfile['restrictions']["prereq"] = \
            [
                [
                    "ENGL 1007",
                    "ENGL 1010",
                    "ENGL 1011"
                ]
            ]

        return True

    return False


with open("not_completed_courses.json", "r") as jsonfile:
    data = json.load(jsonfile)

courses_list = list(data)
output_courses_list = courses_list[:]

for i in courses_list:
    with open(i, "r", encoding='utf-8') as course:

        jsonfile = json.load(course)
        reqs = jsonfile['requirement_description']

        overwrite = detect_all_courses(jsonfile)

        if overwrite:
            with open(i, "w", encoding='utf-8') as writer:
                json.dump(jsonfile, writer, indent=4)

            output_courses_list.remove(i)

            print("Resolved", jsonfile['title'])
            counter += 1


with open("not_completed_courses.json", "w") as jsonfile:
    json.dump(output_courses_list, jsonfile, indent=4)

print(f"{counter} / {len(courses_list)}")
