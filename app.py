from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import face_recognition
import os
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Adjust the width as needed
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Adjust the height as needed
camera.set(cv2.CAP_PROP_FPS, 45)  # Adjust the frame rate as needed

# Path to the folder containing reference images
facedb_path = 'facedb'

def is_image_file(file_path):
    # Check if the file is an image based on the file extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

def load_reference_images():
    reference_images = {}
    for root, dirs, files in os.walk(facedb_path):
        for file in files:
            reference_img_path = os.path.join(root, file)
            if is_image_file(reference_img_path):
                name = os.path.splitext(file)[0]  # Extract the name without extension
                image = face_recognition.load_image_file(reference_img_path)
                reference_images[name] = face_recognition.face_encodings(image)[0]
    return reference_images

reference_encodings = load_reference_images()


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            start_time = time.time()
            is_match, matched_name = recognize_face(frame)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Face recognition time: {execution_time} seconds")

            if is_match:
                cv2.putText(frame, f"MATCH ({matched_name})", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "NO MATCH", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def recognize_face(frame):
    face_locations = face_recognition.face_locations(frame)
    if not face_locations:
        return False, None

    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for encoding in face_encodings:
        for name, reference_encoding in reference_encodings.items():
            result = face_recognition.compare_faces([reference_encoding], encoding)
            if result[0]:
                return True, name

    return False, None




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Process the login form data here
        # Redirect to the main page or another appropriate route
        return redirect(url_for('main'))  # Change this to the desired route
    return render_template('main.html')


@app.route('/addstudent', methods=['GET', 'POST'])
def add_student():
    global captured_images

    if request.method == 'POST':
        if len(captured_images) >= 3:
            return render_template('confirm_images.html', images=captured_images)

        return redirect(url_for('add_student'))

    return render_template('addstudent.html', images=captured_images)


@app.route('/capture', methods=['POST'])
def capture():
    global captured_images

    image_data = request.files['image'].read()
    captured_images.append(base64.b64encode(image_data).decode('utf-8'))

    return "Image captured successfully"


@app.route('/confirm', methods=['POST'])
def confirm():
    # Process and save captured images and student details
    # Redirect to a success page or another appropriate route
    captured_images.clear()
    return "Student added successfully"


@app.route('/video')
def video_stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live')
def video():
    return render_template('live.html')

if __name__ == "__main__":
    app.run(debug=True)
