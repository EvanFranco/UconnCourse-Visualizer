# Courses

Courses should be represented in a database-like format for easy connections (for requirements/schedule building) and filtering (for generic requirements, like a CA or TOI requirement) capabilities. A possible (easy) way of doing this would be creating a giant master JSON file containing a list of courses with all of the fields listed below, structured like in the [ilefa/husky repository.](https://github.com/ilefa/husky/blob/master/courses.json) The main differences from the ilefa json file for the course visualizer would be including separated subject code from course number (for easy filtering/organization) and more specific prerequisite information (for easier flowchart connection). 

JSON file entries should also be able to be updated easily in the future, in case the visualizer is passed off to the UCONN advising team, and they need to add more courses or edit existing courses for the visualizer. 


### Fields

| Field | Type | Example |
| --- | --- | --- | 
| Course Name | `string` | `"CSE 1010"` |
| Department Code | `string` | `"CSE"` |
| Course Number | `int` | `1010` |
| Course Title | `string` | `"Intro to Computing for Engineers"` |
| Course Description | `string` | `"Introduction to computing logic, algorithmic thinking, computing processes, a programming language and computing environment. Knowledge obtained in this course enables use of the computer as an instrument to solve computing problems. Representative problems from science, mathematics, and engineering will be solved."` |
| Credit Count | `int` | `3` |
| Enrollment Requirement Description | `string` | `"May not be taken out of sequence after passing CSE 1729 or 2050."` |
| Restrictions (more info below) | `{ <Restriction Type> : [<Course Name(s)/Credit Count/Major Name/School Name>] }` | `{ 4 : ["CSE 2050"] }` |
| Content Areas | `[string]` | `["CA1", "CA3"]` |
| Topic of Inquiry | `[string]` | `["TOI1", "TOI4"]`
| Skill Code (more info below) | `[char]` | `['W']`
| Lab | `bool` | `true`

> Course name, department code, course number, course title, course description, credit count, enrollment requirement description, CA/TOI, and skill code can likely be scraped easily from the UCONN course catalog website, as they are all formatted consistently. Labs are marked with TOI6-L. Enrollment requirement description is the literal listed restrictions on the UCONN course catalog, while restrictions are standardized by codes (listed below) for easy connections between courses. Restrictions need to be formatted specially, because requirements are formatted differently in text for each course, even if falling under a few certain categories, thus the text after "Enrollment Requirements:" for each course would not be very helpful for connecting courses.


### Restriction Types
> Use enum to abstract identifier

| Restriction Type | Identifier | Example |
| --- | --- | --- |
| Prerequisite | 1 | Course A credit is required to take Course B |
| Concurrent Prerequisite | 2 | Course A is required for Course B, but both may be taken at the same time for credit | 
| Co-requisite | 3 | Course A must be taken at the same time as Course B | 
| Block | 4 | Course A cannot be taken after taking Course B |
| Year/Credit Block | 5 | Course A cannot be taken after X credit amount |
| Recommendation | 6 | Course A is recommended for taking Course B |
| Major Restriction | 7 | Course A is only available to students of majors X, Y, Z |
| School Restriction | 8 | Course A is only available to students in school X |

### Skill Codes
| Code Type | Identifier | Example |
| --- | --- | --- |
| Writing | `"W"` | `"CSE 4947W"` |
| Quantitiative | `"Q"` | `"MATH 1132Q"` |
| Environmental Literacy | `"E"` | `"NRE 1000E"` |

# Majors, Minors, Concentrations

Effectively, majors and minors are sets of courses for a student to take for a degree. So, Majors, Minors, Concentrations are represented as course packs, and each have a credit requirement (number of credits needed to achieve)
Majors and minors also inherit course requirements from the Common Curriculum and the School which they are a part of (example: College of Engineering for Computer Science). 
A user major/major + concentration/minor selection should correspond to a course pack object that tells the flowchart generator which courses to connect.

### Course Packs

A course pack is effectively a set of course requirements to add to the flowchart pool (the courses the flowchart generator must connect). A course pack can have requirement types as shown in the table below. The course pack should be a collection of requirements to get credit for the major, minor, or concentration it represents. Each index of the requirements collection should be an individual requirement, with the requirement implementations listed in the table below. Each index is itself a collection of choices for that requirement.

| Requirement Type | Example | Implementation | 
| --- | --- | --- |
| Simple | Course A credit is required for the course pack. | `["CSE 1010"]` |
| Choice | Course A or Course B credit is required for the course pack | `["MATH 3160", "STAT 3025Q", "STAT 3345Q", "STAT 3375Q"]` |
| Complex Choice | (Course A and Course B) or (Course C and Course D) credits are required for the course pack | `[["ME 4972", "ME 4973W"], ["ME 4975", "ME 4974W", "ME 4976"]]` |
| Additional Complex Choice | Limits on which courses of which department codes can be taken (ex. only 3 credits from DEPT can apply to X requirement) | Mark choice with `*` to alert user to check the catalog for specific pick restrictions |
| Elective(s) / Professional Requirements | 6 credits from 2000-level or higher DEPT courses are required for the course pack | `[<SQL/database filter query>, <int> (credit count)]` |


