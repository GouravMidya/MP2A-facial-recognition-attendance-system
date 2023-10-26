import os
import face_recognition

# Declared Variables
facedb_path = 'facedb'
reference_encodings = {}

#checks if a given file path represents an image file

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
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    reference_encodings[name] = encodings[0]
                else:
                    print(f"No face found in {name}'s reference image.")
    return reference_encodings