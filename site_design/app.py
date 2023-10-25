from flask import Flask, json, render_template, request, flash, redirect, url_for,session
import mysql.connector

# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendify"
)

db_cursor = db_connection.cursor()

# Fetch classroom data from the database
def get_classrooms():
    db_cursor.execute("SELECT ClassroomID, Year, Division, Branch FROM Classrooms")
    classrooms = db_cursor.fetchall()
    return classrooms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'it is what it is manas'

@app.route('/', methods=['GET','POST'] )
def index():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        try:
            db_cursor.execute("SELECT * FROM teachers WHERE Email = '"+email+"';")
            val = db_cursor.fetchall()
            if (email==val[0][2] and password==val[0][3]):
                session['message'] = 'Logged in successfully!'
                session['teacher_id'] = val[0][0]
                print(session['teacher_id'])
                session['teacher_name'] = val[0][1]
                return redirect(url_for('dashboard'))
        except:
            session['message'] = 'Login failed'
    return render_template('index.html')

@app.route('/attendance_summary')
def attendance_summary():
    # Read data from the CSV file
    attendance_data = []
    with open(excel_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            attendance_data.append(row)

    # Pass the data to the template
    return render_template('attendance_summary.html', attendance_data=attendance_data)


@app.route('/dashboard')
def dashboard():
    # Retrieve TeacherID from the session
    teacher_id = session.get('teacher_id', None)
    teacher_name = session.get('teacher_name',None)
    # Fetch classroom data
    classrooms = get_classrooms()
    print(classrooms)
    # Pass the success message and TeacherID to the template
    return render_template('dashboard.html', message=session.pop('message', ''), teacher_id=teacher_id,teacher_name=teacher_name,classrooms_json=json.dumps(classrooms))

if __name__ == "__main__":
    app.run(debug=True)