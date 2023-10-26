import mysql.connector
from datetime import datetime
import csv

# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendify"
)

db_cursor = db_connection.cursor()

db_cursor.execute("delete from classrooms")

# List of records to insert
classroom_records = [
    (2023, 'A', 'COMPS'),
    (2023, 'B', 'COMPS'),
    (2023, 'C', 'COMPS'),
    (2022, 'A', 'IT'),
    (2022, 'B', 'IT'),
    (2022, 'C', 'COMPS'),
]

# SQL INSERT statement to insert all records in one go
insert_query = "INSERT INTO Classrooms (Year, Division, Branch) VALUES (%s, %s, %s)"



# Execute the INSERT statement with the list of records
db_cursor.executemany(insert_query, classroom_records)

db_cursor.execute("delete from Subjects")

# List of records to insert for subjects
subjects_records = [
    ('Mathematics'),
    ('Science'),
    ('History'),
    ('English'),
    ('Art')
]

# SQL INSERT statement to insert all records into the Subjects table
insert_query = "INSERT INTO Subjects (name) VALUES (%s)"

# Execute the INSERT statement with the list of records
db_cursor.executemany(insert_query, subjects_records)

# Fetch classroom data from the database
def get_classrooms_and_subjects():
    db_cursor.execute("SELECT ClassroomID, Year, Division, Branch FROM Classrooms")
    classrooms = db_cursor.fetchall()
    db_cursor.execute("SELECT name FROM Subjects")
    subjects = db_cursor.fetchall()
    return classrooms,subjects

# Excel Sheet :
now= datetime.now()
current_date=now.strftime("%Y-%m-%d")

classrooms,subjects=get_classrooms_and_subjects()

for i in range(len(classrooms)):
    for j in range(len(subjects)):
        print(classrooms[i])
        print(subjects[j])
        
excel_filename=current_date+'.csv'

f= open(excel_filename,'w+',newline='')
lnwriter = csv.writer(f)

