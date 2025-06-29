import random
from faker import Faker

fake = Faker()

# Initialize lists to store generated IDs
department_ids = []
student_ids = []
course_ids = []
instructor_ids = []

# Generate Departments data
departments = [
    ("Computer Science", "CS"),
    ("Electrical Engineering", "EE"),
    ("Mechanical Engineering", "ME"),
    ("Civil Engineering", "CE"),
    ("Chemical Engineering", "CHE")
]

department_insert = "INSERT INTO Departments (department_name, department_code) VALUES\n"
for dept_name, dept_code in departments:
    department_insert += f"('{dept_name}', '{dept_code}'),\n"
department_insert = department_insert.rstrip(',\n') + ';\n\n'

# Generate Courses data
courses = []
course_insert = "INSERT INTO Courses (course_code, course_name, department_id, is_core) VALUES\n"
for i in range(20):
    dept_id = random.randint(1, len(departments))
    course_code = f"{departments[dept_id-1][1]}{random.randint(100, 499)}"
    course_name = fake.catch_phrase()
    is_core = random.choice([True, False])
    courses.append((course_code, course_name, dept_id, is_core))
    course_insert += f"('{course_code}', '{course_name}', {dept_id}, {is_core}),\n"
course_insert = course_insert.rstrip(',\n') + ';\n\n'

# Generate Students data
student_insert = "INSERT INTO Students (first_name, last_name, email, department_id) VALUES\n"
for i in range(100):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
    dept_id = random.randint(1, len(departments))
    student_insert += f"('{first_name}', '{last_name}', '{email}', {dept_id}),\n"
student_insert = student_insert.rstrip(',\n') + ';\n\n'

# Generate Instructors data
instructor_insert = "INSERT INTO Instructors (first_name, last_name, email, department_id) VALUES\n"
for i in range(20):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
    dept_id = random.randint(1, len(departments))
    instructor_insert += f"('{first_name}', '{last_name}', '{email}', {dept_id}),\n"
instructor_insert = instructor_insert.rstrip(',\n') + ';\n\n'

# Generate Enrollments data
enrollment_insert = "INSERT INTO Enrollments (student_id, course_id, semester, year) VALUES\n"
for i in range(200):
    student_id = random.randint(1, 100)
    course_id = random.randint(1, 20)
    semester = random.choice(['Fall', 'Spring', 'Summer'])
    year = random.randint(2020, 2023)
    enrollment_insert += f"({student_id}, {course_id}, '{semester}', {year}),\n"
enrollment_insert = enrollment_insert.rstrip(',\n') + ';\n\n'

# Generate TeachingAssignments data
teaching_insert = "INSERT INTO TeachingAssignments (instructor_id, course_id, semester, year) VALUES\n"
for i in range(50):
    instructor_id = random.randint(1, 20)
    course_id = random.randint(1, 20)
    semester = random.choice(['Fall', 'Spring', 'Summer'])
    year = random.randint(2020, 2023)
    teaching_insert += f"({instructor_id}, {course_id}, '{semester}', {year}),\n"
teaching_insert = teaching_insert.rstrip(',\n') + ';\n\n'

# Combine all INSERT statements
all_inserts = department_insert + course_insert + student_insert + instructor_insert + enrollment_insert + teaching_insert

with open("data.sql", "w") as file:
    file.write(all_inserts)

print(all_inserts)