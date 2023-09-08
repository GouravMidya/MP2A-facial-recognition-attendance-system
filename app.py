from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import base64
from deepface import DeepFace
import threading
import os

app = Flask(__name__)
camera = cv2.VideoCapture(0)
captured_images = []

# Initialize the cascade classifier
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')



face_cap = cv2.CascadeClassifier("C:/Users/admin/AppData/Local/Programs/Python/Python311/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture( cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0 

face_match = False

reference_img1 = cv2.imread('face-db\Prathamesh Naik\prathamesh1.jpg')
reference_img2 = cv2.imread('face-db\Prathamesh Naik\prathamesh2.jpg')
ref = [reference_img1,reference_img2]



def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            is_match = recognize_face(frame)

            if is_match:
                cv2.putText(frame, "MATCH", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "NO MATCH", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def recognize_face(frame):
    global captured_images

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Convert the captured image to base64
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')

        if len(captured_images) > 0:
            for image_data in captured_images:
                result = DeepFace.verify(image_data, frame_data, model_name="VGG-Face")
                if result['verified']:
                    return True

    return False



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
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
