from flask import Flask, render_template, Response
import cv2
import face_recognition
from multiprocessing import Process, Queue, Pipe
import os
import time
import multiprocessing

app = Flask(__name__)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
camera.set(cv2.CAP_PROP_FPS, 30)

facedb_path = 'facedb'
reference_encodings = {}

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


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            is_match, matched_names = recognize_face(frame)
            if is_match:
                text = f"MATCH ({', '.join(matched_names)})"
                cv2.putText(frame, text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Update or initialize timers for matched faces
                for name in matched_names:
                    if name not in presence_timers:
                        presence_timers[name] = time.time()
                    else:
                        elapsed_time = time.time() - presence_timers[name]
                        if elapsed_time >= 2:
                            print(f"{name} marked as present after 2 seconds")
                            # Here you can perform any action to mark the person as present
            else:
                cv2.putText(frame, "NO MATCH", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

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

    with Process() as face_recognition_process:
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

@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/video')
def video_stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')