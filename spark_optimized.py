import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Set up Spark session
spark = SparkSession.builder \
    .appName("MongoDB Integration") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/ass1") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/ass1") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# Load collections with optimizations
departments_df = spark.read.format("mongo").option("collection", "departments").load().cache()
courses_df = spark.read.format("mongo").option("collection", "courses").load().cache()
students_df = spark.read.format("mongo").option("collection", "students").load().cache()
instructors_df = spark.read.format("mongo").option("collection", "instructors").load().cache()

# 1. Fetching all students enrolled in a specific course using predicate pushdown
def fetch_students_in_course(course_code):
    # Use MongoDB's aggregation pipeline for filtering in MongoDB to reduce data transfer
    students_df_filtered = spark.read.format("mongo").option("collection", "students") \
        .option("pipeline", f'[{{"$match": {{"enrollments.course_code": "{course_code}"}}}}]').load()
    return students_df_filtered.select("first_name", "last_name", "email", "enrollments.course_code")

# 2. Calculating the average number of students enrolled in courses offered by a particular instructor
def avg_students_per_instructor(instructor_id):
    # Broadcast instructors_df to avoid shuffling
    instructor_courses = broadcast(instructors_df.filter(col("_id") == instructor_id)) \
        .select(explode("courses_taught").alias("course"))
    return instructor_courses.select(explode("course.semesters").alias("semester")) \
        .select(avg("semester.num_students").alias("avg_students")).first()["avg_students"]

# 3. Listing all courses offered by a specific department
def courses_in_department(department_code):
    return departments_df.filter(col("code") == department_code) \
        .select(explode("courses").alias("course")) \
        .select("course.code", "course.name")

# 4. Finding the total number of students per department
def students_per_department():
    return departments_df.select("_id", "name", "total_students")

# 5. Finding instructors who have taught all the BTech CSE core courses
def instructors_teaching_all_cse_core():
    # Fetch the CSE department
    cse_department = departments_df.filter(col("code") == "CS").first()

    # Get the list of CSE core courses
    cse_core_courses = [course["code"] for course in cse_department["courses"] if course["is_core"]]

    # Use broadcast join for smaller instructors_df
    exploded_instructors = broadcast(instructors_df) \
        .withColumn("name", concat_ws(" ", col("first_name"), col("last_name"))) \
        .select("name", explode("courses_taught.course_code").alias("course_code"))

    # Filter instructors who have taught all core CSE courses
    instructors = exploded_instructors \
        .filter(col("course_code").isin(cse_core_courses)) \
        .groupBy("name").agg(collect_set("course_code").alias("taught_courses")) \
        .filter(size(col("taught_courses")) == len(cse_core_courses))

    return instructors

# 6. Finding top-10 courses with the highest enrollments
def top_courses_by_enrollment():
    # Use MongoDB pipeline to sort and limit in MongoDB
    top_courses = spark.read.format("mongo").option("collection", "courses") \
        .option("pipeline", '[{"$sort": {"total_enrollments": -1}}, {"$limit": 10}]') \
        .load()
    return top_courses.select("_id", "code", "name", "total_enrollments")

# Measure query execution time
def measure_query_execution(query_func, *args):
    start_time = time.time()
    result_df = query_func(*args)
    result_df.show()  # Trigger query
    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time

# Dictionary to store query execution times
execution_times = {}

# Measure and store execution times for each query
print("1. Students enrolled in course 'EE244':")
execution_times['Students in EE244'] = measure_query_execution(fetch_students_in_course, "EE244")

print("\n2. Average students per course for instructor with ID '1':")
start_time = time.time()
avg_students = avg_students_per_instructor(1)
end_time = time.time()
print(avg_students)
execution_times['Average students per instructor'] = end_time - start_time

print("\n3. Courses offered by department 'CS':")
execution_times['Courses in department CS'] = measure_query_execution(courses_in_department, "CS")

print("\n4. Total students per department:")
execution_times['Students per department'] = measure_query_execution(students_per_department)

print("\n5. Instructors who have taught all BTech CSE core courses:")
execution_times['Instructors teaching all CSE core courses'] = measure_query_execution(instructors_teaching_all_cse_core)

print("\n6. Top 10 courses by enrollment:")
execution_times['Top 10 courses by enrollment'] = measure_query_execution(top_courses_by_enrollment)

# Print the stored execution times
print("\nExecution Times (in seconds):")
for query, exec_time in execution_times.items():
    print(f"{query}: {exec_time:.2f} seconds")

# Save execution times to a file
with open("optimized_execution_times.txt", "w") as file:
    file.write("Execution Times (in seconds):\n")
    for query, exec_time in execution_times.items():
        file.write(f"{query}: {exec_time:.2f} seconds\n")

# Stop the Spark session
spark.stop()
