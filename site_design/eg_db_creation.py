import mysql.connector

# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
)

# Create a database named 'attendify' if it doesn't exist
db_cursor = db_connection.cursor()
db_cursor.execute("CREATE DATABASE IF NOT EXISTS attendify")
db_cursor.close()

# Connect to the 'attendify' database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendify"
)

# Create tables
db_cursor = db_connection.cursor()

# Create Teachers Table
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Teachers (
        TeacherID INT AUTO_INCREMENT PRIMARY KEY,
        FullName VARCHAR(255) NOT NULL,
        Email VARCHAR(255) NOT NULL UNIQUE,
        Password VARCHAR(255) NOT NULL
    )
""")

# Create Admins Table
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Admins (
        AdminID INT AUTO_INCREMENT PRIMARY KEY,
        FullName VARCHAR(255) NOT NULL,
        Email VARCHAR(255) NOT NULL UNIQUE,
        Password VARCHAR(255) NOT NULL
    )
""")

# Create Classrooms Table
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Classrooms (
        ClassroomID INT AUTO_INCREMENT PRIMARY KEY,
        Year INT NOT NULL,
        Division VARCHAR(50) NOT NULL,
        Branch VARCHAR(50) NOT NULL,
        HomeroomTeacher INT,
        FOREIGN KEY (HomeroomTeacher) REFERENCES Teachers(TeacherID)
    )
""")

# Create Assigned Classrooms Table (Many-to-Many)
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssignedClassrooms (
        AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
        TeacherID INT,
        ClassroomID INT,
        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
        FOREIGN KEY (ClassroomID) REFERENCES Classrooms(ClassroomID)
    )
""")

# Create Students Table
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        StudentID INT AUTO_INCREMENT PRIMARY KEY,
        FullName VARCHAR(255) NOT NULL,
        Email VARCHAR(255),
        RollNo INT,
        PersonalDetails TEXT,
        StudentImage VARCHAR(255)
    )
""")

# Create Attendance Records Table
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS AttendanceRecords (
        RecordID INT AUTO_INCREMENT PRIMARY KEY,
        Date DATE NOT NULL,
        Classroom INT,
        Subject VARCHAR(255) NOT NULL,
        Teacher INT,
        Student INT,
        AttendanceStatus VARCHAR(50) NOT NULL,
        FOREIGN KEY (Classroom) REFERENCES Classrooms(ClassroomID),
        FOREIGN KEY (Teacher) REFERENCES Teachers(TeacherID),
        FOREIGN KEY (Student) REFERENCES Students(StudentID)
    )
""")

# Commit changes and close the connection
db_connection.commit()
db_connection.close()
