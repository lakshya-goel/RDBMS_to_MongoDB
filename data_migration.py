import psycopg2
from pymongo import MongoClient
from psycopg2.extras import RealDictCursor

# PostgreSQL connection
pg_conn = psycopg2.connect(
    dbname="a1",
    user="postgres",
    password="lak",
    host="localhost"
)

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["ass1"]

def extract_from_postgres(query):
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()

def transform_departments(departments, courses):
    department_courses = {}
    for course in courses:
        department_id = course["department"]["_id"]
        if department_id not in department_courses:
            department_courses[department_id] = []
        department_courses[department_id].append({
            "_id": course["_id"],
            "code": course["code"],
            "name": course["name"],
            "is_core": course["is_core"]
        })

    return [{
        "_id": dep["department_id"],
        "name": dep["department_name"],
        "code": dep["department_code"],
        "total_students": 0,  # Will be updated later
        "courses": department_courses.get(dep["department_id"], [])
    } for dep in departments]

def transform_courses(courses):
    return [{
        "_id": course["course_id"],
        "code": course["course_code"],
        "name": course["course_name"],
        "department": {
            "_id": course["department_id"],
            "name": course["department_name"],
            "code": course["department_code"]
        },
        "is_core": course["is_core"],
        "total_enrollments": 0,  # Will be updated later
        "offerings": []  # Will be populated later
    } for course in courses]

def transform_students(students, enrollments):
    student_enrollments = {}
    for enrollment in enrollments:
        if enrollment["student_id"] not in student_enrollments:
            student_enrollments[enrollment["student_id"]] = []
        student_enrollments[enrollment["student_id"]].append({
            "course_id": enrollment["course_id"],
            "course_code": enrollment["course_code"],
            "course_name": enrollment["course_name"],
            "semester": enrollment["semester"],
            "year": enrollment["year"]
        })
    
    return [{
        "_id": student["student_id"],
        "first_name": student["first_name"],
        "last_name": student["last_name"],
        "email": student["email"],
        "department": {
            "_id": student["department_id"],
            "name": student["department_name"],
            "code": student["department_code"]
        },
        "enrollments": student_enrollments.get(student["student_id"], [])
    } for student in students]

def transform_instructors(instructors, teaching_assignments):
    instructor_courses = {}
    for assignment in teaching_assignments:
        if assignment["instructor_id"] not in instructor_courses:
            instructor_courses[assignment["instructor_id"]] = {}
        
        course_id = assignment["course_id"]
        if course_id not in instructor_courses[assignment["instructor_id"]]:
            instructor_courses[assignment["instructor_id"]][course_id] = {
                "course_id": course_id,
                "course_code": assignment["course_code"],
                "course_name": assignment["course_name"],
                "is_core": assignment["is_core"],
                "semesters": []
            }
        
        instructor_courses[assignment["instructor_id"]][course_id]["semesters"].append({
            "semester": assignment["semester"],
            "year": assignment["year"],
            "num_students": 0  # Will be updated later
        })
    
    return [{
        "_id": instructor["instructor_id"],
        "first_name": instructor["first_name"],
        "last_name": instructor["last_name"],
        "email": instructor["email"],
        "department": {
            "_id": instructor["department_id"],
            "name": instructor["department_name"],
            "code": instructor["department_code"]
        },
        "courses_taught": list(instructor_courses.get(instructor["instructor_id"], {}).values())
    } for instructor in instructors]

def load_to_mongodb(collection, data):
    if data:
        mongo_db[collection].insert_many(data)

def update_enrollments():
    pipeline = [
        {"$unwind": "$enrollments"},
        {"$group": {
            "_id": "$enrollments.course_id",
            "total_enrollments": {"$sum": 1}
        }}
    ]
    course_enrollments = list(mongo_db.students.aggregate(pipeline))
    
    for course in course_enrollments:
        mongo_db.courses.update_one(
            {"_id": course["_id"]},
            {"$set": {"total_enrollments": course["total_enrollments"]}}
        )

def update_department_student_count():
    pipeline = [
        {"$group": {
            "_id": "$department._id",
            "total_students": {"$sum": 1}
        }}
    ]
    department_counts = list(mongo_db.students.aggregate(pipeline))
    
    for dept in department_counts:
        mongo_db.departments.update_one(
            {"_id": dept["_id"]},
            {"$set": {"total_students": dept["total_students"]}}
        )

def update_course_offerings():
    pipeline = [
        {"$unwind": "$enrollments"},
        {"$group": {
            "_id": {
                "course_id": "$enrollments.course_id",
                "semester": "$enrollments.semester",
                "year": "$enrollments.year"
            },
            "num_students": {"$sum": 1}
        }}
    ]
    course_offerings = list(mongo_db.students.aggregate(pipeline))
    
    for offering in course_offerings:
        mongo_db.courses.update_one(
            {"_id": offering["_id"]["course_id"]},
            {"$push": {
                "offerings": {
                    "semester": offering["_id"]["semester"],
                    "year": offering["_id"]["year"],
                    "num_students": offering["num_students"]
                }
            }}
        )

def main():
    # Extract data from PostgreSQL
    departments = extract_from_postgres("SELECT * FROM departments")
    courses = extract_from_postgres("""
        SELECT c.*, d.department_name, d.department_code
        FROM Courses c
        JOIN departments d ON c.department_id = d.department_id
    """)
    students = extract_from_postgres("""
        SELECT s.*, d.department_name, d.department_code
        FROM Students s
        JOIN departments d ON s.department_id = d.department_id
    """)
    enrollments = extract_from_postgres("""
        SELECT e.*, c.course_code, c.course_name
        FROM Enrollments e
        JOIN courses c ON e.course_id = c.course_id
    """)
    instructors = extract_from_postgres("""
        SELECT i.*, d.department_name, d.department_code
        FROM Instructors i
        JOIN departments d ON i.department_id = d.department_id
    """)
    teaching_assignments = extract_from_postgres("""
        SELECT ta.*, c.course_code, c.course_name, c.is_core
        FROM TeachingAssignments ta
        JOIN Courses c ON ta.course_id = c.course_id
    """)

    # Transform data
    transformed_courses = transform_courses(courses)
    transformed_departments = transform_departments(departments, transformed_courses)
    transformed_students = transform_students(students, enrollments)
    transformed_instructors = transform_instructors(instructors, teaching_assignments)

    # Load data into MongoDB
    load_to_mongodb("departments", transformed_departments)
    load_to_mongodb("courses", transformed_courses)
    load_to_mongodb("students", transformed_students)
    load_to_mongodb("instructors", transformed_instructors)

    # Update derived data
    update_enrollments()
    update_department_student_count()
    update_course_offerings()

    print("Data migration completed successfully!")

if __name__ == "__main__":
    main()
    pg_conn.close()
    mongo_client.close()