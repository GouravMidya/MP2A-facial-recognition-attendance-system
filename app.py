from flask import Flask, render_template, Response, json, render_template, request, flash, redirect, url_for,session
import cv2
import face_recognition
from multiprocessing import Process, Queue, Pipe
import os
import time
import multiprocessing
import mysql.connector
from flask_socketio import SocketIO, emit


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

# Fetch classroom data from the database
def get_classrooms():
    db_cursor.execute("SELECT ClassroomID, Year, Division, Branch FROM Classrooms")
    classrooms = db_cursor.fetchall()
    return classrooms

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
camera.set(cv2.CAP_PROP_FPS, 30)

facedb_path = 'facedb'
reference_encodings = {}
present = []
# Maintain a dictionary to track the presence of individuals and their timers
presence_timers = {}


def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)


def load_reference_images():
    for root, dirs, files in os.walk(facedb_path):
        for file in files:
            reference_img_path = os.path.join(root, file)
            if is_image_file(reference_img_path):
                name = os.path.splitext(file)[0]
                image = face_recognition.load_image_file(reference_img_path)
                reference_encodings[name] = face_recognition.face_encodings(image)[0]


load_reference_images()

presence_timers = {} 

def generate_frames():
    global present

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            is_match, matched_names = recognize_face(frame)

            # Initialize a dictionary to keep track of faces in the current frame
            current_frame_faces = {}

            if is_match:
                text = f"MATCH ({', '.join(matched_names)})"
                cv2.putText(frame, text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                for name in matched_names:
                    if name not in presence_timers:
                        presence_timers[name] = {'start_time': time.time(), 'duration': 0}
                    else:
                        elapsed_time = time.time() - presence_timers[name]['start_time']

                        if elapsed_time >= 10:
                            # Here you can perform any action to mark the person as present
                            present.append(name)
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

            # Other parts of your code...

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            socketio.emit('update_present', {'present': present})
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def recognize_face(frame):
    face_locations = face_recognition.face_locations(frame, model="hog")
    if not face_locations:
        return False, []

    face_encodings = face_recognition.face_encodings(frame, face_locations)
    recognized_names = []

    for encoding in face_encodings:
        for name, reference_encoding in reference_encodings.items():
            result = face_recognition.compare_faces([reference_encoding], encoding)
            if result[0]:
                recognized_names.append(name)

    return bool(recognized_names), recognized_names


def face_recognition_worker(fi, fl):
    while True:
        small_frame = fi.get()
        print("Running face recognition process")
        face_locations = face_recognition.face_locations(small_frame, model="hog")

        if len(face_locations) > 0:
            print(face_locations)
            for (top7, right7, bottom7, left7) in face_locations:
                small_frame_c = small_frame[top7:bottom7, left7:right7]
                fl.send(small_frame_c)


if __name__ == "__main__":
        multiprocessing.set_start_method('spawn')
        video_input = 0

        num_processes = 2  # Set the number of processes

        #with Process() as face_recognition_process:
        fi = Queue(maxsize=14)
        parent_p, child_p = Pipe()

        processes = []
        for _ in range(num_processes):
            process = Process(target=face_recognition_worker, args=(fi, child_p))
            process.start()
            processes.append(process)

        app.run(debug=True, threaded=True)

        frame_id = 0
        fps_var = 0

        while True:
            ret, frame = camera.read()
            effheight, effwidth = frame.shape[:2]
            if effwidth < 20:
                break

            xxx = 930
            yyy = 10/16
            small_frame = cv2.resize(frame, (xxx, int(xxx*yyy)))

            if frame_id % 2 == 0:
                if not fi.full():
                    fi.put(small_frame)

                    cv2.imshow('Video', small_frame)

                    print("FPS: ", int(1.0 / (time.time() - fps_var)))
                    fps_var = time.time()

            frame_id += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup: Terminate worker processes
        for process in processes:
            process.terminate()


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
                session['message'] = 'Login failed'
        except Exception as e:
            print("Login failed:", str(e))
            session['message'] = 'Login failed'

    return render_template('index.html')


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


@app.route('/dashboard')
def dashboard():
    # Retrieve TeacherID from the session
    teacher_id = session.get('teacher_id', None)
    teacher_name = session.get('teacher_name',None)
    # Fetch classroom data
    classrooms = get_classrooms()
    print(classrooms)
    # Pass the success message and TeacherID to the template
    #return render_template('dashboard.html', message=session.pop('message', ''), teacher_id=teacher_id,teacher_name=teacher_name,classrooms_json=json.dumps(classrooms))
    
    # Corrected line in your Flask application
    video_feed = url_for('video_feed')

    return render_template('dashboard.html', message=session.pop('message', ''),
                           teacher_id=teacher_id, teacher_name=teacher_name,
                           classrooms_json=json.dumps(classrooms), video_feed=video_feed, present=present)


# In your Flask application
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('update_present_request')
def handle_update_present_request():
    emit('update_present', {'present': present})

if __name__ == "__main__":
    # ... (existing code)

    # Start Flask and SocketIO
    socketio.run(app, debug=True)