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



def manual_set_requirements(current_course: Course):
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------")
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

    while (restriction_type != "f"):
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
                limit = input(
                    "Enter credit range, separated by commas, or enter semester range, separated by \"-\" \n\t")
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

        print(
            "--------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"{current_course.name} Current restrictions: \n{json.dumps(current_course.restrictions, indent=4)}\n")
        cont = input(f"Restriction description: {current_course.requirement_description} \nMore restrictions? Y/N\n\t")
        if (cont == "N"):
            break

        print(options_str)
        restriction_type = input()
        # print current restrictions added