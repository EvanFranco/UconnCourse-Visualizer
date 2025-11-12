# Courses

Courses should be represented in a database-like format for easy connections (for requirements/schedule building) and filtering (for generic requirements, like a CA or TOI requirement) capabilities. A possible (easy) way of doing this would be creating a giant master JSON file with all of the fields listed below in them (like in the [ilefa/husky repo](https://github.com/ilefa/husky/blob/master/courses.json)). 

> Note: I personally don't know how easy filtering by name/code/etc would be with a JSON file. A SQL database (possibly implemented as an SQLite database) would be a good way to enable filtering for generic elective requirements.

### Fields

| Field | Type | Example |
| --- | --- | --- | 
| Course Name | `string` | `"CSE 1010"` |
| Subject Code | `string` | `"CSE"` |
| Course Title | `string` | `"Intro to Computing for Engineers"` |
| Credit Count | `int` | `3` |
| Restrictions | `{ <Restriction (int)> : <Course Name> } ` | `{ 4 : "CSE 2050" } ` |
| Content Areas | `[string]` | `["CA1, CA3]` |
| Topic of Inquiry | `[string]` | `["TOI1", "TOI4"]`
| Skill Code | `[char]` | `["W"]`
| Lab | `bool` | `true`


### Restriction Types
> Use enum to abstract away identifier

| Restriction Type | Identifier | Example |
| --- | --- | --- |
| Requirement | 1 | Course A credit is required to take Course B |
| Concurrent Requirement | 2 | Course A is required for Course B, but both may be taken at the same time for credit | 
| Co-requisite | 3 | Course A must be taken at the same time as Course B | 
| Block | 4 | Course A cannot be taken after taking Course B |
| Year Block | 5 | Course A cannot be taken after X credit amount |
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


