import face_recognition
import cv2
import numpy as np
import os
import json
import time
import speech_recognition as sr
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk

# Initialize the recognizer
r = sr.Recognizer()

encodings_file = "encodings.json"
faces_folder = "Faces_stored"
known_faces = {}

# Ensure faces folder exists
os.makedirs(faces_folder, exist_ok=True)

# Load known faces
if os.path.exists(encodings_file):
    with open(encodings_file, "r") as f:
        known_faces = json.load(f)
    print(f"✅ Loaded {len(known_faces)} known faces.")
else:
    print("ℹ️ No known faces file. Loading images from folder...")
    for filename in os.listdir(faces_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(faces_folder, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                name = os.path.splitext(filename)[0]
                known_faces[name] = encodings[0].tolist()
                print(f"✅ Encoded face for: {name}")
            else:
                print(f"⚠️ No face found in {filename}")
    with open(encodings_file, "w") as f:
        json.dump(known_faces, f)
    print(f"💾 Saved {len(known_faces)} known faces to '{encodings_file}'.")


def save_encodings():
    with open(encodings_file, "w") as f:
        json.dump(known_faces, f)
    print("✅ Encodings saved.")


def register_user(name, cap):
    if name in known_faces:
        confirm = input(f"⚠️ '{name}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Registration cancelled.")
            return

    while True:
        print(f"📸 Capturing photo for {name}...")

        snapshot_taken = [False]
        frame_container = [None]

        def show_camera(canvas, label):
            while not snapshot_taken[0]:
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_container[0] = frame.copy()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.configure(image=imgtk)
                time.sleep(0.03)

        def take_snapshot():
            snapshot_taken[0] = True
            root.destroy()

        root = tk.Tk()
        root.title("Capture Face")
        root.attributes("-topmost", True)

        video_label = tk.Label(root)
        video_label.pack()

        tk.Label(root, text="Click the button below to take your picture").pack(pady=5)
        tk.Button(root, text="Take Picture", command=take_snapshot).pack(pady=10)

        Thread(target=show_camera, args=(root, video_label)).start()
        root.mainloop()

        frame = frame_container[0]
        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) == 1:
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            known_faces[name] = face_encoding.tolist()

            save_path = os.path.join(faces_folder, f"{name}.jpg")
            cv2.imwrite(save_path, frame)
            print(f"📸 Saved face image to '{save_path}'")
            print(f"✅ Registered new face: {name}")

            save_encodings()
            break
        elif len(face_locations) == 0:
            print("❌ No face found. Please try again.")
        else:
            print("⚠️ Multiple faces detected. Please ensure only one face is visible and try again.")


def confirm_name_from_audio():
    name = ""
    while not name:
        with sr.Microphone() as source:
            print("🔊 Please say your name: ")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            temp_name = text.capitalize().strip()
            confirm = input(f"You said: '{temp_name}'. Is this correct? (y/n): ").strip().lower()
            if confirm == 'y':
                name = temp_name
            else:
                print("❌ Let's try again.")
        except sr.UnknownValueError:
            print("Could not understand audio. Try again.")
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
            name = input("Enter your name: ").strip()
    return name


def recognize_face():
    print("⏳ Starting in 3 seconds...")
    time.sleep(3)
    cap = cv2.VideoCapture(0)
    last_confirmed_name = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, boxes)

        for (top, right, bottom, left), face_encoding in zip(boxes, face_encodings):
            name = "Unknown"
            matches = face_recognition.compare_faces(
                [np.array(enc) for enc in known_faces.values()], face_encoding)
            face_distances = face_recognition.face_distance(
                [np.array(enc) for enc in known_faces.values()], face_encoding)

            if matches and min(face_distances) < 0.6:
                best_match_index = np.argmin(face_distances)
                name = list(known_faces.keys())[best_match_index]

            if name != "Unknown":
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if name != last_confirmed_name:
                    print(f"👤 Detected: {name}")
                    response = input(f"👤 Are you '{name}'? (y/n): ").strip().lower()
                    if response == "y":
                        print(f"✅ Welcome, {name}!")
                        last_confirmed_name = name
                    else:
                        print("❌ Face mismatch. Registering new face...")
                        new_name = confirm_name_from_audio()
                        register_user(new_name, cap)
                        last_confirmed_name = new_name

                        # Show face recognition preview again on top
                        cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
                        cv2.setWindowProperty("Face Recognition", cv2.WND_PROP_TOPMOST, 1)

                    break
            else:
                print("❓ Face not recognized.")
                new_name = confirm_name_from_audio()
                if new_name and new_name.lower() not in ["skip", "exit"]:
                    register_user(new_name, cap)
                    last_confirmed_name = new_name

                    # Show face recognition preview again on top
                    cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
                    cv2.setWindowProperty("Face Recognition", cv2.WND_PROP_TOPMOST, 1)
                break

        cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face Recognition", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Start app
print("🎉 Face Recognition App")
recognize_face()