# Importing all necessary modules
from flask import Flask, render_template, Response, render_template, request, redirect, url_for,session, jsonify,send_file, flash
import cv2
import csv
import face_recognition
from multiprocessing import Process, Queue, Pipe
import os
import time
import multiprocessing
import mysql.connector
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime
from imagin import load_reference_images
import gc
import pandas as pd
from io import BytesIO

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'your_secret_key_here'



# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="20032003",
    database="attendify"
)
db_cursor = db_connection.cursor()



# Defining a global variable for location of photos 
UPLOAD_FOLDER = 'facedb'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Excel Sheet :
now= datetime.now()
current_date=now.strftime("%Y-%m-%d")



# Declared Global Variables
facedb_path = 'facedb'
reference_encodings = {}
present = []
presence_timers = {} # Maintain a dictionary to track the presence of individuals and their timers
global student_name
global student_email
global student_data
current_section = "P1"
global excel_filename
global path
path="cache"
excel_filename= None
f= open(current_date+'.csv','w+',newline='')
lnwriter = csv.writer(f)
global halt
reference_encodings_loaded = False  # Add this global flag

# Function for generating Frames 

def generate_frames():
    #Configuring the camera for 320x240 resolution at 30 FPS using OpenCV.
    halt=3
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    camera.set(cv2.CAP_PROP_FPS, 30)
    global reference_encodings, reference_encodings_loaded
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            if not reference_encodings_loaded:
                present.clear()
                reference_encodings = load_reference_images()
                reference_encodings_loaded = True

            is_match, matched_names = recognize_face(frame)

            # Initialize a dictionary to keep track of faces in the current frame
            current_frame_faces = {}

            for name in matched_names:
                # Concatenate matched names into a single string with newlines
                matched_names_text = ' | '.join(matched_names)

                # Set the font scale for smaller text
                font_scale = 0.8

                # Get the size of the text
                text_size = cv2.getTextSize(matched_names_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0]

                # Calculate the position for centering the text
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = 30

                # Put the text on the frame
                cv2.putText(frame, matched_names_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)

                if name not in presence_timers:
                    presence_timers[name] = {'start_time': time.time(), 'duration': 0}
                else:
                    
                    elapsed_time = time.time() - presence_timers[name]['start_time']
                    # Check if a face has been detected for at least 7 seconds the first time the 3 seconds

                    if elapsed_time >= halt:
                        present.append(name)
                        halt=3
                        # Save the recognized face image
                        face_locations = face_recognition.face_locations(frame)
                        for face_location in face_locations:
                            save_recognized_face(frame, face_location, name)
                        
                        del reference_encodings[name]
                        presence_timers[name]['start_time'] = time.time()
                        presence_timers[name]['duration'] = 0
                    else:
                        presence_timers[name]['duration'] = elapsed_time

                # Mark this face as present in the current frame
                current_frame_faces[name] = True

            # Reset timers for faces not detected in the current frame
            for name in presence_timers.keys():
                if name not in current_frame_faces:
                    presence_timers[name]['start_time'] = time.time()
                    presence_timers[name]['duration'] = 0

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Send the updated present list to the client to display in textarea
            socketio.emit('update_present', {'present': present})


            #Creating a multipart HTTP response to stream JPEG frames with frame delimiters and content type headers.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



# Function for Face Recognition

def recognize_face(frame):
    # Find face locations in the frame using the HOG model.
    face_locations = face_recognition.face_locations(frame, model="hog")

    # If no face locations are found, return no recognition.
    if not face_locations:
        return False, []

    # Extract face encodings for the located faces.
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    recognized_names = []

    for i, encoding in enumerate(face_encodings):
        for name, reference_encoding in reference_encodings.items():
            result = face_recognition.compare_faces([reference_encoding], encoding)

            # If a match is found, add the recognized name to the list.
            if result[0]:
                recognized_names.append(name)


    # Return True if any faces were recognized and the recognized names.
    return bool(recognized_names), recognized_names



# Function for face recog workers

def face_recognition_worker(fi, fl):

    #Configuring the camera for 320x240 resolution at 30 FPS using OpenCV.
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    camera.set(cv2.CAP_PROP_FPS, 30)
    while True:
        # Get the small frame from the input queue.
        small_frame = fi.get()
        # Detect face locations in the small frame using the HOG model.
        face_locations = face_recognition.face_locations(small_frame, model="hog")

        # If any face locations are found, process and send them.
        if len(face_locations) > 0:
            for (top7, right7, bottom7, left7) in face_locations:
                # Extract the face region from the small frame.
                small_frame_c = small_frame[top7:bottom7, left7:right7]

                 # Send the cropped face region to the output queue.
                fl.send(small_frame_c)



# Function to Update Student Attendance

def update_attendance(student_id):
    db_cursor.execute("UPDATE Students SET Attendance = Attendance + 1 WHERE StudentID = %s", (student_id,))
    db_connection.commit()
        


# Function to Submit Student details :

def submit_student():
    if request.method == 'POST':
        student_name = request.form.get('studentName')
        student_email = request.form.get('studentEmail')

        session['student_name'] = student_name
        session['student_email'] = student_email

        # Get the uploaded image data
        student_image = request.form.get('studentImage')  # This assumes that the image data is sent as part of the form data

        # Insert the student data into the database
        db_cursor.execute("INSERT INTO Students (FullName, Email) VALUES (%s, %s)",
                           (student_name, student_email))
        db_connection.commit()

        # You can add any additional logic or redirects here

        return redirect(url_for('dashboard'))  # Redirect to the dashboard after submission

    # Handle GET request or any other cases
    return redirect(url_for('dashboard'))  # Redirect to the dashboard after submission


# Check if ip file is jpg or png

def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)



# Function to add recognized image to folder

def save_recognized_face(frame, face_location, name):
    top, right, bottom, left = face_location
    # Crop the face from the frame
    face_image = frame
    
    # Define a directory to save the recognized face images (e.g., 'recognized_faces')
    recognized_faces_dir = './static/recognized_faces/'+path
    
    if not os.path.exists(recognized_faces_dir):
        os.makedirs(recognized_faces_dir)
    
    # Construct the file path for the saved image
    image_filename = f'{name}.jpg'
    image_path = os.path.join(recognized_faces_dir, image_filename)
    
    # Save the recognized face image
    cv2.imwrite(image_path, face_image)
    
    # Return the image path
    return image_path

    

# Socket :

@socketio.on('update_present_request')
def handle_update_present_request():
    emit('update_present', {'present': present})



# Save image in Folder

def save_face_from_base64(image_data):
    try:
        sql_query = "SELECT StudentID, FullName, Email, image_name FROM Students"
        db_cursor.execute(sql_query)
        student_data = db_cursor.fetchall()
        for student_record in student_data:
            id=student_record[0]
            student_name = student_record[1]
            student_email = student_record[2]
            image_name = student_record[3]

        if not student_name or not student_email:
            # Handle the case where student_name and student_email are not available
            print('Missing student_name or student_email in the session')
            return

        # Decode the base64 image data
        image_data_decoded = base64.b64decode(image_data.split(',')[1])

        # Save the image directly without further processing
        with open(os.path.join(app.config['UPLOAD_FOLDER'], f"{student_name}_{id}.png"), 'wb') as img_file:
            img_file.write(image_data_decoded)

        # Update the "image_name" field in the database
        db_cursor.execute("SELECT StudentID FROM Students WHERE Email = %s and FullName = %s;", (student_email, student_name))
        id = db_cursor.fetchone()
        image_name = f"{student_name}_{id[0]}"
        db_cursor.execute("UPDATE Students SET image_name = %s WHERE StudentID = %s", (image_name, id[0]))
        db_connection.commit()

        print('Face saved:', image_name)

    except Exception as e:
        print('Error processing face:', str(e))



def generate_csv_filename(classroom, subject):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d")  # Format the current time as a string
    filename = f"Attendance_Records/{current_time}-{classroom}-{subject}.csv"
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer
        csv_writer = csv.writer(csvfile)
    return filename



# Main Function Begins Here :

if __name__ == "__main__":
    # Set the start method for multiprocessing to 'spawn'.
    multiprocessing.set_start_method('spawn')
    
    num_processes = 2  # Set the number of processes

    # Create a queue for passing frames to worker processes.
    fi = Queue(maxsize=14)
    
    # Create a parent-child Pipe for communication with worker processes.
    parent_p, child_p = Pipe()

    processes = []

    # Start worker processes for face recognition.
    for _ in range(num_processes):
        process = Process(target=face_recognition_worker, args=(fi, child_p))
        process.start()
        processes.append(process)

    # Start the application (e.g., a web-based video stream).
    app.run(debug=True, threaded=True)


# Generate Reports
def combine_attendance(class_name, subject_name):
    # Define the directory where CSV files are stored
    data_dir = r"/Users/prathameshnaik/Desktop/MP2A-facial-recognition-attendance-system/Attendance_Records"  # Directory path of location where we are saving csv files

    # List of CSV files for the selected class and subject
    csv_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            # Check if the file name matches the pattern "date-class-subject.csv"
            if file.endswith(f"-{class_name}-{subject_name}.csv"):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        return None  # No matching files found

    # Create a dictionary to store attendance data
    attendance_data = {}

    for file in csv_files:
        date = file.split("/")[-1].split(".")[0]  # Extract the date from the file name
        df = pd.read_csv(file, header=None)  # Specify header=None to read without column headers

        # Remove the image name column by dropping the last column
        df = df.iloc[:, :-1]
        # Rename the attendance status column with the date
        df = df.rename(columns={df.columns[-1]: date})

        # Set the index to the first column (studentid)
        df = df.set_index(df.columns[0])

        if date in attendance_data:
            attendance_data[date] = pd.concat([attendance_data[date], df], axis=1, join="outer")
        else:
            attendance_data[date] = df

    # Create a list of DataFrames and concatenate them by index
    df_list = list(attendance_data.values())
    combined_df = pd.concat(df_list, axis=1, join="outer")
    
    # Use groupby and aggregate to ensure that name and email columns appear only once
    combined_df = combined_df.groupby(level=0, axis=1).first()
    combined_df = combined_df.rename(columns={df.columns[0]: "Name"})
    combined_df = combined_df.rename(columns={df.columns[1]: "Email"})

        
    return combined_df



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# ALL ROUTES DEFINED HERE : --



# Login Page or Landing page 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        try:
            db_cursor.execute("SELECT * FROM teachers WHERE Email = %s;", (email,))
            val = db_cursor.fetchone()
            if val and password == val[3]:  # Use integer index to access 'Password'
                session['message'] = 'Logged in successfully!'
                session['teacher_id'] = val[0]  # Use integer index to access 'TeacherID'
                session['teacher_name'] = val[1]  # Use integer index to access 'FullName'
                return redirect(url_for('dashboard'))
            else:
                flash('Username and password do not match', 'error')  # Store an error message
        except Exception as e:
            print("Login failed:", str(e))

    return render_template('index.html')



# Signup Page
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            db_cursor.execute("INSERT INTO teachers (FullName, Email, Password) VALUES (%s, %s, %s)",
                              (full_name, email, password))
            db_connection.commit()

            session['message'] = 'Signup successful! Please login.'
            return redirect(url_for('index'))
        except Exception as e:
            print("Signup failed:", str(e))
            session['message'] = 'Signup failed'

    return render_template('index.html')



# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global reference_encodings_loaded
    global excel_filename
    global path
    # Initialize current_section with a default value
    current_section = "P1"

    # Retrieve TeacherID from the session
    teacher_id = session.get('teacher_id', None)
    teacher_name = session.get('teacher_name', None)

    sql_query = "SELECT ClassroomID, Year, Division FROM Classrooms"
    db_cursor.execute(sql_query)
    classrooms = db_cursor.fetchall()
    
    sql_query = "SELECT name FROM subjects"
    db_cursor.execute(sql_query)
    subjects = db_cursor.fetchall()    
            
    sql_query = "SELECT StudentID, FullName, Email, image_name, Attendance, TotalAttendance FROM Students"
    db_cursor.execute(sql_query)
    student_data = db_cursor.fetchall()
    # Corrected line in your Flask application
    video_feed = url_for('video_feed')


    if request.method == 'POST':
        classroom = request.form.get('classroom')
        print(classroom)
        subject = request.form.get('subject')
        print(subject)
        path=classroom+"_"+subject
        excel_filename = generate_csv_filename(classroom, subject)
        session['excel_filename'] = excel_filename  # Store it in the session
        current_section = "P2"
        path=current_date+"_"+classroom+"_"+subject
        reference_encodings_loaded = False  # Reset the flag when classroom/subject changes

        
    return render_template('dashboard.html', message=session.pop('message', ''), teacher_id=teacher_id, teacher_name=teacher_name, reference_encodings=reference_encodings, video_feed=video_feed, present=present, student_data=student_data, classrooms=classrooms, subjects=subjects, current_section=current_section)



# Attendance Summary

@app.route('/attendance_summary', methods=['GET', 'POST'])
def attendance_summary():
    attendance_data = []
    # Get the excel_filename from the session
    excel_filename = session.get('excel_filename')
    
    # Check if excel_filename is available
    if excel_filename:
        if os.path.exists(excel_filename):
            # Proceed with processing and reading the CSV file
            with open(excel_filename, newline='') as csvfile:  # Use 'r' for reading
                reader = csv.reader(csvfile)  # Create a CSV reader

                # Read data from the CSV file
                for row in reader:
                    attendance_data.append(row)

    sql_query = "SELECT StudentID, FullName, Email, image_name FROM Students"
    db_cursor.execute(sql_query)
    student_data = db_cursor.fetchall()
    db_cursor.execute("UPDATE Students SET TotalAttendance = TotalAttendance + 1")
    db_connection.commit()
    for student_record in student_data:
        student_id = student_record[0]
        student_name = student_record[1]
        student_email = student_record[2]
        image_name = student_record[3]
        if image_name in present:
            status = 'P'  # Mark the student as present
            update_attendance(student_id)
        else:
            status = 'A'  # Mark the student as absent
            # Open the existing CSV file in append mode
        with open(excel_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            student_with_status = [student_id, student_name, student_email, status,image_name]
            csv_writer.writerow(student_with_status)
            csvfile.flush()  # Flush the buffer to ensure the data is written immediately
            os.fsync(csvfile.fileno())  # Ensure the data is written to disk

    # Read data from the updated CSV file
    attendance_data = []  # You don't need to redefine this
    with open(excel_filename, newline='') as csvfile:  # Use 'r' for reading
        reader = csv.reader(csvfile)  # Create a CSV reader
        for row in reader:
            attendance_data.append(row)

    present.clear()  # Clear the list of present students
    return render_template('attendance_summary.html', attendance_data=attendance_data,image_name=image_name,path=path)



# Video Feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# ADD STUDENT ROUTES(2) :
# API route to save the image from addstudent
@app.route('/save-image', methods=['POST'])
def save_image():
    try:
        data = request.get_json()
        image_data = data.get('imageData')
        # Call the save_face_from_base64 function
        save_face_from_base64(image_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        print('Error saving image:', str(e))
        return jsonify({'status': 'error'})



# Submit Student data from Add student
@app.route('/submit-student', methods=['POST'])
def submit_student_route():
    return submit_student()



# View Attendance 
@app.route('/viewattendance', methods=['POST'])
def viewattendance():
    classroom = request.form.get('classroom')
    subject = request.form.get('subject')
    date = request.form.get('date')
    # Specify the path to your pre-existing CSV file
    csv_filename = 'Attendance_Records/'+date +'-'+classroom+'-'+subject+'.csv'
    if os.path.isfile(csv_filename):
        # The file exists, so you can proceed to read its contents
        # Read data from the CSV file
        attendance_data = []
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                attendance_data.append(row)
        
        return render_template('attendance_summary.html', attendance_data=attendance_data)
    
    else:
        # The file does not exist, handle this situation as per your requirements
        return "<h1>Attendance record not found.</h1>"


# About Page Route
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')



# Generate Reports routes

@app.route('/combine', methods=['POST'])
def combine():
    class_name = request.form.get('class')
    subject_name = request.form.get('subject')
    if class_name and subject_name:
        combined_data = combine_attendance(class_name, subject_name)
        
        if combined_data is not None:
            # Convert the DataFrame to an Excel file
            excel_output = BytesIO()
            with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
                combined_data.to_excel(writer, sheet_name='Combined Attendance', index=False)
            excel_output.seek(0)

            # Send the Excel file to the user for download
            return send_file(excel_output, as_attachment=True, download_name=f"{class_name}_{subject_name}_attendance.xlsx")
    return "Please select a class and subject."



@app.route('/generate_reports')
def generate_reports():
    sql_query = "SELECT ClassroomID, Year, Division FROM Classrooms"
    db_cursor.execute(sql_query)
    classrooms = db_cursor.fetchall()
    
    sql_query = "SELECT name FROM subjects"
    db_cursor.execute(sql_query)
    subjects = db_cursor.fetchall()    
            
    return render_template('generate.html', classrooms=classrooms, subjects=subjects)


# Route to handle the submission of the form for adding a class
@app.route('/add_class', methods=['POST'])
def add_class():
    if request.method == 'POST':
        #class_name = request.form['class_name']
        year = request.form['year']
        division = request.form['division']
        branch = request.form['branch']

        # Connect to the MySQL database
        conn = mysql.connector.connect(host="localhost",
    user="root",
    password="20032003",
    database="attendify")#insert
        cursor = conn.cursor()

        # Insert the class into the database
        insert_query = "INSERT INTO Classrooms (Year, Division, Branch) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (year, division, branch))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Redirect to a success page or display a success message
        return "Class added successfully"
    


# Route to display the HTML form for adding a class
@app.route('/add_classsub', methods=['GET'])
def add_class_form():
    return render_template('add_classsub.html')



# Route to handle the submission of the form for adding a subject
@app.route('/add_subject', methods=['POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['subject_name']

        # Connect to the MySQL database
        conn = mysql.connector.connect(host="localhost",
    user="root",
    password="20032003",
    database="attendify")
        cursor = conn.cursor()

        # Insert the subject into the database
        insert_query = "INSERT INTO subjects (name) VALUES (%s)"
        cursor.execute(insert_query, (subject_name,))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Redirect to a success page or display a success message
        return "Subject added successfully"
    

    # Route to handle image upload
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image = request.files['image']
        student_name=session['student_name'] 
        student_email=session['student_email'] 
        db_cursor.execute("SELECT StudentID FROM Students WHERE Email = %s and FullName = %s;", (student_email, student_name))
        id = db_cursor.fetchone()
        image_name = f"{student_name}_{id[0]}"
        if image.filename != '':
            # Save the image to the "uploads" folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], (image_name)+'.png'))
            return 'Image uploaded successfully.'

    return 'Image not uploaded.'