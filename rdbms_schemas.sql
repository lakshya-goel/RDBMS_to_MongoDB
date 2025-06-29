-- Students table
CREATE TABLE Students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_id INTEGER NOT NULL
);

-- Courses table
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL,
    is_core BOOLEAN NOT NULL
);

-- Enrollments table
CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL
);

-- Instructors table
CREATE TABLE Instructors (
    instructor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_id INTEGER NOT NULL
);

-- Departments table
CREATE TABLE Departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL,
    department_code VARCHAR(10) UNIQUE NOT NULL
);

-- TeachingAssignments table
CREATE TABLE TeachingAssignments (
    assignment_id SERIAL PRIMARY KEY,
    instructor_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL
);

-- Add foreign key constraints
ALTER TABLE Students
ADD CONSTRAINT fk_student_department
FOREIGN KEY (department_id) REFERENCES Departments(department_id);

ALTER TABLE Courses
ADD CONSTRAINT fk_course_department
FOREIGN KEY (department_id) REFERENCES Departments(department_id);

ALTER TABLE Enrollments
ADD CONSTRAINT fk_enrollment_student
FOREIGN KEY (student_id) REFERENCES Students(student_id),
ADD CONSTRAINT fk_enrollment_course
FOREIGN KEY (course_id) REFERENCES Courses(course_id);

ALTER TABLE Instructors
ADD CONSTRAINT fk_instructor_department
FOREIGN KEY (department_id) REFERENCES Departments(department_id);

ALTER TABLE TeachingAssignments
ADD CONSTRAINT fk_teaching_instructor
FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id),
ADD CONSTRAINT fk_teaching_course
FOREIGN KEY (course_id) REFERENCES Courses(course_id);

-- Add indexes for better query performance
CREATE INDEX idx_student_department ON Students(department_id);
CREATE INDEX idx_course_department ON Courses(department_id);
CREATE INDEX idx_enrollment_course ON Enrollments(course_id);
CREATE INDEX idx_enrollment_student ON Enrollments(student_id);
CREATE INDEX idx_instructor_department ON Instructors(department_id);
CREATE INDEX idx_teaching_instructor ON TeachingAssignments(instructor_id);
CREATE INDEX idx_teaching_course ON TeachingAssignments(course_id);
