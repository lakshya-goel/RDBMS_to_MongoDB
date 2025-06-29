# PostgreSQL to MongoDB Migration and Spark Query Optimization

## 📌 Project Overview

This project demonstrates the full cycle of migrating a relational PostgreSQL database to a document-oriented MongoDB schema, running analytical queries with Apache Spark, and optimizing query performance with advanced techniques.

---

## 🗂️ Relational Schema

**Key Tables:**
- **Students**: Student details.
- **Courses**: Course details.
- **Enrollments**: Links students and courses.
- **Instructors**: Instructor details.
- **Departments**: Department details.
- **TeachingAssignments**: Links instructors with courses taught.

---

## 📄 MongoDB Schema Design

The MongoDB schema is designed to optimize query performance by:
- **Denormalization**: Related data is embedded to reduce joins.
- **Embedding**: For example, enrollments are embedded within student documents.
- **Indexing**: Frequently queried fields are indexed.

**Collections:**
- **departments**
- **students**
- **instructors**
- **courses**

Each collection embeds related data for faster queries.

---

## ⚙️ Data Migration Pipeline

**Steps:**
1. **Extract**: Data is extracted from PostgreSQL using `psycopg2` and SQL queries.
2. **Transform**: Data is transformed to match the MongoDB schema (embedded documents, denormalized fields).
3. **Load**: Data is inserted into MongoDB using `pymongo`.

**Post-Load Updates**:
- Calculate total enrollments per course.
- Calculate total students per department.

---

## 🔍 Key Queries Implemented (Apache Spark)

Queries implemented using PySpark with the MongoDB Spark Connector:

1. 📚 **Fetch students enrolled in a specific course**
2. 📊 **Calculate average number of students per instructor**
3. 📜 **List all courses offered by a department**
4. 🧮 **Find total students per department**
5. 👩‍🏫 **Identify instructors who taught all BTech CSE core courses**
6. 🏆 **Find top 10 courses by enrollment**

---

## 🚀 Performance Optimization

**Techniques Applied:**
- **Predicate Pushdown**: Filters data in MongoDB before Spark reads it.
- **Broadcast Joins**: Broadcast smaller DataFrames in Spark to speed up joins.
- **MongoDB Indexing**:
  - `enrollments.course_code`
  - `courses.total_enrollments`
  - `instructors.courses_taught.course_code`

**Results:**  
Execution times improved by 20–35% after optimizations.

---

## ⚡ Pre vs. Post Optimization Performance

| Query                              | Pre-Optimization | Post-Optimization |
|------------------------------------|------------------|-------------------|
| Students in Course EE244           | 1.92s            | 1.34s             |
| Avg Students per Instructor        | 0.97s            | 0.76s             |
| Courses Offered by Department CS   | 0.24s            | 0.19s             |
| Students per Department            | 0.14s            | 0.12s             |
| Instructors Teaching All Core CSE  | 0.64s            | 0.51s             |
| Top 10 Courses by Enrollment       | 0.20s            | 0.13s             |

---

## ✅ Key Takeaways

- Data embedding and denormalization greatly reduce the need for expensive joins.
- Apache Spark integrates well with MongoDB for large-scale analytics.
- Optimization strategies like predicate pushdown, broadcasting, and indexing significantly enhance performance.

---

## 📚 Technologies Used

- **PostgreSQL**
- **MongoDB**
- **Apache Spark**
- **Python (pyspark, psycopg2, pymongo)**

---

## 🔗 How to Run

1. **Set up PostgreSQL and MongoDB.**
2. **Run ETL scripts to migrate data.**
3. **Run Spark jobs to query MongoDB collections.**
4. **Apply optimizations and compare performance.**

---

## 📌 Author

This project was implemented as part of a data engineering and analytics exploration.

---

**Happy Querying! 🚀**
