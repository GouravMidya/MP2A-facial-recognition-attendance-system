import mysql.connector

# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="20032003",
    database="attendify"
)

db_cursor = db_connection.cursor()

# Insert sample records into Teachers table
teachers_data = [
    ("John Smith", "john@example.com", "password1"),
    ("Alice Johnson", "alice@example.com", "password2")
]

for teacher in teachers_data:
    query = "INSERT INTO Teachers (FullName, Email, Password) VALUES (%s, %s, %s)"
    db_cursor.execute(query, teacher)

# Commit changes to the Teachers table
db_connection.commit()

# Insert sample records into Classrooms table
classrooms_data = [
    (2023, "A", "Science", 1),  # Assigning the first teacher to the first classroom
    (2023, "B", "Math", 2)     # Assigning the second teacher to the second classroom
]

for classroom in classrooms_data:
    query = "INSERT INTO Classrooms (Year, Division, Branch, HomeroomTeacher) VALUES (%s, %s, %s, %s)"
    db_cursor.execute(query, classroom)

# Commit changes and close the connection
db_connection.commit()
db_connection.close()
