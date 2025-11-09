# soul_sync_gui.py

import sqlite3
import speech_recognition as sr
import keyboard
import time
import cohere
import pyttsx3
import threading
import cv2
import numpy as np
import os
from keras.models import load_model
import tkinter as tk
import serial
from tkinter import messagebox, ttk, scrolledtext
from PIL import Image, ImageTk
import shutil
# === SETTINGS ===
dataset_path = 'dataset'
model_path = 'trainer.yml'
label_file = 'labels.txt'
os.makedirs(dataset_path, exist_ok=True)

# === MODELS & INIT ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if not os.path.exists("D:\\coding\\emotion_counselor_bot\\emotion_detection_model.h5"):
    raise FileNotFoundError("Emotion model not found.")
else:
    emotion_model = load_model("D:\\coding\\emotion_counselor_bot\\emotion_detection_model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
recognizer = sr.Recognizer()
mic = sr.Microphone()
co = cohere.Client("M66iWrfF8fpc6sz5Yl5k3IYyiBiF8BQ6f40RLmwp")

# === DATABASE ===
conn = sqlite3.connect("therapist_bot.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    name TEXT,
    age INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    question TEXT,
    emotion TEXT,
    answer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id))''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        date TEXT NOT NULL,
        conversation TEXT NOT NULL
    )
''')
conn.commit()


# === SPEECH ===
def speak_text(text):
    engine = pyttsx3.init()
    
    # Select Zira voice if available
    voices = engine.getProperty('voices')
    for v in voices:
        if "zira" in v.name.lower():
            engine.setProperty('voice', v.id)
            break

    engine.setProperty('rate', 145)
    engine.setProperty('volume', 1.0)

    # Queue and run full text once
    engine.say(text)
    engine.runAndWait()
    engine.stop()



# === FACE RECOG ===
def register_face(username):
    cam = cv2.VideoCapture(1)
    count = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            cv2.imwrite(f"{dataset_path}/{username}_{count}.jpg", face_img)
        if count >= 20:
            break
    cam.release()
    cv2.destroyAllWindows()

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels, label_dict = [], [], {}
    current_label = 0
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            for line in f:
                label, username = line.strip().split(":")
                label_dict[username] = int(label)
        current_label = max(label_dict.values()) + 1
    for file in os.listdir(dataset_path):
        if file.endswith(".jpg"):
            img = cv2.imread(os.path.join(dataset_path, file), cv2.IMREAD_GRAYSCALE)
            username = file.split("_")[0]
            if username not in label_dict:
                label_dict[username] = current_label
                current_label += 1
            faces.append(img)
            labels.append(label_dict[username])
    recognizer.train(faces, np.array(labels))
    recognizer.save(model_path)
    with open(label_file, 'w') as f:
        for username, label in label_dict.items():
            f.write(f"{label}:{username}\n")

def recognize_face():
    if not os.path.exists(model_path): return None, None
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)
    labels = {}
    with open(label_file, 'r') as f:
        for line in f:
            label, username = line.strip().split(":")
            labels[int(label)] = username
    cam = cv2.VideoCapture(1)
    recognized_username = None
    timeout = time.time() + 10
    while time.time() < timeout:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            label, confidence = recognizer.predict(face_img)
            if confidence < 70:
                recognized_username = labels[label]
                break
        if recognized_username:
            break
    cam.release()
    cv2.destroyAllWindows()
    if recognized_username:
        cursor.execute("SELECT name FROM users WHERE username=?", (recognized_username,))
        result = cursor.fetchone()
        if result:
            return recognized_username, result[0]
    return None, None

# === EMOTION ===
def detect_facial_emotion():
    emotions_detected = []
    start_time = time.time()
    cap = cv2.VideoCapture(1)
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
            roi = np.expand_dims(np.expand_dims(roi, -1), 0)
            pred = emotion_model.predict(roi)[0]
            emotions_detected.append(emotion_labels[np.argmax(pred)])
    cap.release()
    cv2.destroyAllWindows()
    return max(set(emotions_detected), key=emotions_detected.count) if emotions_detected else "Neutral"

# === BOT ===
def get_ai_response(prompt_text, emotion):
    prompt = (
    f"You are a thoughtful, emotionally intelligent Indian therapist who helps students cope with stress, fear, academic pressure, and self-doubt. "
    f"The student has shared a concern, and an emotion has been detected.\n\n"
    f"Emotion: {emotion}\n"
    f"Student's Message: \"{prompt_text}\"\n\n"
    f"Respond with a short, wise, human-like answer. Your reply must:\n"
    f"- Be a **fully complete paragraph** (1 short sentence- like a reply in a chat).\n"
    f"- Address both the emotion and the exact issue in the message.\n"
    f"- Avoid sympathy clichés like 'I'm sorry you're going through this'.\n"
    f"- Avoid giving half sentences, unfinished thoughts, or abrupt endings.\n"
    f"- Sound calm, honest, and mature — like a real therapist.\n"
    f"- Provide one practical, comforting insight or suggestion.\n"
    f"Always answer in complete, clear sentences, even if the user's input is short or fragmented.\n"
    f"Your response:"
    )

    
    
    
    response = co.generate(model='command', prompt=prompt, temperature=0.6)
    return response.generations[0].text.strip()

#def record_until_space_and_process():
    #print("Listening... Press SPACE to stop and process your question.")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_data = []

        def listen_background():
            try:
                while not keyboard.is_pressed('space'):
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    audio_data.append(audio)
            except sr.WaitTimeoutError:
                pass  # No speech in timeout window
            except:
                pass  # Ignore other exceptions

        listen_thread = threading.Thread(target=listen_background)
        listen_thread.start()

        while not keyboard.is_pressed('space'):
            time.sleep(0.1)

        listen_thread.join()

    if audio_data:
        combined = audio_data[0]
        for a in audio_data[1:]:
            combined = sr.AudioData(
                combined.frame_data + a.frame_data,
                combined.sample_rate,
                combined.sample_width
            )
        return combined
    else:
        return None


# === GUI ===
class SoulSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soul-Sync Therapist Bot")
        self.root.state('zoomed')
        self.root.bind("<Escape>", lambda event: self.root.attributes('-fullscreen', False))
        self.root.configure(bg="#f0f4f8")
        self.username = None
        self.name = None
        self.create_welcome()
        self.is_listening = False
        self.recording = False
        self.audio_data = None

        #self.audio_chunks = []

    def create_welcome(self):
        for widget in self.root.winfo_children(): widget.destroy()
        frame = tk.Frame(self.root, bg="#e0eafc")
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Welcome to Soul Sync",
         font=("Lucida Calligraphy", 42, "bold"),
         fg="#2c3e50",
         bg="#e0eafc",
         bd=0, relief="flat").pack(pady=60)

        tk.Label(frame, text="Connecting Hearts with AI", 
         font=("Helvetica", 20), fg="#7f8c8d", bg="#e0eafc").pack(pady=(0, 40))

        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        start_btn = tk.Button(
            frame,
            text="Start",
            font=("Helvetica", 20, "bold"),
            bg="#4CAF50",         # Green button
            fg="white",           # White text
            padx=30,              # Wide button
            pady=15,              # Tall button
            relief="raised",      # 3D button style
            bd=4,                 # Border thickness
            activebackground="#45a049",  # Darker green on click
            cursor="hand2",       # Hand cursor on hover
            command=self.identify_user
        )
        start_btn.pack(pady=30)

    # Voice greeting after the window appears
        def intro_speech():
            speak_text("Hi")
            time.sleep(0.5)
            speak_text("Welcome to Soul Sync")
            time.sleep(0.8)
            speak_text("Please look at the camera and click Start.")
        self.root.after(1000, intro_speech)  # Delays speech slightly so UI renders first


    def identify_user(self):
        #speak_text("Please look at the camera for identification.")
        username, name = recognize_face()
        if username:
            self.username = username
            self.name = name.title()
            speak_text(f"Welcome {name}")
            self.create_main_menu()
        else:
            speak_text("Welcome. New users must register.")
            self.create_register()

    def create_register(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f4f6f8", padx=30, pady=30)
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame, text="Register New User",
            font=("Helvetica", 24, "bold"),
            bg="#f4f6f8", fg="#2c3e50"
        ).pack(pady=20)

        form_frame = tk.Frame(frame, bg="#f4f6f8")
        form_frame.pack(pady=10)

        label_style = {"font": ("Helvetica", 14), "bg": "#f4f6f8", "anchor": "w"}
        entry_style = {"font": ("Helvetica", 14), "width": 30}

        tk.Label(form_frame, text="Username", **label_style).grid(row=0, column=0, pady=5, sticky="w")
        self.reg_username = tk.Entry(form_frame, **entry_style)
        self.reg_username.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Full Name", **label_style).grid(row=1, column=0, pady=5, sticky="w")
        self.reg_name = tk.Entry(form_frame, **entry_style)
        self.reg_name.grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Age", **label_style).grid(row=2, column=0, pady=5, sticky="w")
        self.reg_age = tk.Entry(form_frame, **entry_style)
        self.reg_age.grid(row=2, column=1, pady=5)

        btn_frame = tk.Frame(frame, bg="#f4f6f8")
        btn_frame.pack(pady=30)

        btn_style = {
            "font": ("Helvetica", 14),
            "bg": "#4CAF50",
            "fg": "white",
            "activebackground": "#45a049",
            "width": 20,
            "bd": 3,
            "relief": "ridge",
            "cursor": "hand2"
        }

        tk.Button(btn_frame, text="Register", command=self.save_registration, **btn_style).grid(row=0, column=0, padx=20)
        tk.Button(btn_frame, text="Return to Start", command=self.create_welcome, **btn_style).grid(row=0, column=1, padx=20)

    def delete_user_profile(self, username):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your profile? This action cannot be undone.")
        if not confirm:
            return

        try:
            # 1. Delete from database
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            cursor.execute("DELETE FROM sessions WHERE username=?", (username,))
            conn.commit()

            # 2. Count and delete user's image folder
            # 2. Delete user's face images only (keep folder)
            # 2. Delete user's face images from the dataset folder
            deleted_files = 0
            for file in os.listdir(dataset_path):
                if file.startswith(f"{username}_") and file.lower().endswith((".jpg", ".jpeg", ".png")):
                    os.remove(os.path.join(dataset_path, file))
                    deleted_files += 1
            print(f"Deleted file: {file}")


            # 3. Retrain model
            train_model()

            speak_text("Your profile has been deleted.")
            messagebox.showinfo("User Deleted", f"Deleted user '{username}' and {deleted_files} face images.")
            self.create_start_screen()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_registration(self):
        username = self.reg_username.get().strip()
        name = self.reg_name.get().strip()
        age = self.reg_age.get().strip()

        if not username or not name or not age:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return

        try:
            cursor.execute("INSERT INTO users (username, name, age) VALUES (?, ?, ?)", (username, name, age))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists.")
            return

        # Show loading message
        # Show loading message
        loading_label = tk.Label(self.root, text="Preparing face registration...",
                                font=("Helvetica", 12), bg="#f4f6f8", fg="gray")
        loading_label.pack(pady=10)
        self.root.update()

        # ✅ Speak before camera starts
        speak_text("Taking face samples for registration. Please look at the camera and remain still.")

        # Update label while registering face
        loading_label.config(text="Capturing face images... Please look at the camera.")
        self.root.update()

        # Register and train
        register_face(username)
        train_model()

        # Remove label when done
        loading_label.destroy()


        # Final step
        speak_text(f"Registered successfully. Welcome {name}")

        self.username = username
        self.name = name
        self.create_main_menu()


    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#e2f0cb")
        frame.pack(expand=True, fill="both")

        # Cursive font for the name (like 'Lucida Handwriting', fallback if not available)
        try:
            font_name = ("Lucida Handwriting", 22, "bold")
        except:
            font_name = ("Helvetica", 22, "bold")

        tk.Label(frame, text=f"Welcome, {self.name}", font=font_name, bg="#e2f0cb", fg="#2e4053").pack(pady=30)

        button_style = {
            "font": ("Helvetica", 16),
            "width": 30,
            "height": 2,
            "bg": "#a3d2ca",
            "fg": "#1b262c",
            "activebackground": "#5eaaa8"
        }
        delete_label = tk.Label(frame, text="Delete My Profile", font=("Arial", 9), fg="blue", bg="#f4f6f8", cursor="hand2")
        delete_label.bind("<Button-1>", lambda e: self.delete_user_profile(self.username))
        delete_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Bottom-right with padding

        tk.Button(frame, text="1. Take Therapy", command=self.therapy_screen, **button_style).pack(pady=10)
        tk.Button(frame, text="2. View Previous Sessions", command=self.view_history, **button_style).pack(pady=10)
        tk.Button(frame, text="3. Exit", command=self.root.quit, **button_style).pack(pady=10)
    def therapy_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.conversation_active = True

        frame = tk.Frame(self.root, bg="#fbeec1", padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame,
            text="Therapy Session",
            font=("Helvetica", 22, "bold"),
            bg="#fbeec1",
            fg="#333"
        ).pack(pady=(10, 20))

        btn_frame = tk.Frame(frame, bg="#fbeec1")
        btn_frame.pack(pady=10)

        btn_style = {
            "font": ("Helvetica", 14),
            "width": 18,
            "height": 2,
            "bg": "#ffd6a5",
            "fg": "#333",
            "activebackground": "#ffb085",
            "bd": 2,
            "relief": "ridge",
            "cursor": "hand2"
        }

        tk.Button(btn_frame, text="Detect Emotion", command=self.detect_emotion, **btn_style).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Start Conversation", command=self.start_listening, **btn_style).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(btn_frame, text="Stop Talking", command=self.stop_and_respond, **btn_style).grid(row=0, column=2, padx=10, pady=5)

        tk.Button(btn_frame, text="End Conversation", command=self.end_conversation, **btn_style).grid(row=0, column=3, padx=10, pady=5)

        response_frame = tk.LabelFrame(frame, text="Therapist Response", bg="#fff9ec", fg="#333", font=("Helvetica", 14, "bold"), bd=3, relief="groove")
        response_frame.pack(fill="both", expand=True, pady=20)

        self.response_box = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD, font=("Helvetica", 12), bg="#ffffff", fg="#000", padx=10, pady=10)
        self.status_label = tk.Label(frame, text="", font=("Helvetica", 12), bg="#fbeec1", fg="darkgreen")
        self.status_label.pack()

        self.response_box.pack(fill="both", expand=True)

        tk.Button(frame, text="Back to Menu", command=self.create_main_menu, **btn_style).pack(pady=10)
        self.current_emotion = "Neutral"    





    def stop_and_respond(self):
        self.recording = False  # Stops the loop in capture_audio_chunks
        if self.listen_thread:
            self.listen_thread.join()

        # Combine all audio chunks
        if self.audio_chunks:
            combined = self.audio_chunks[0]
            for chunk in self.audio_chunks[1:]:
                combined = sr.AudioData(
                    combined.frame_data + chunk.frame_data,
                    combined.sample_rate,
                    combined.sample_width
                )
            self.audio_data = combined
            self.status_label.config(text="Done Listening.")
        else:
            self.audio_data = None
            self.status_label.config(text="No speech captured.")

        # Recognize and respond
        try:
            user_text = recognizer.recognize_google(self.audio_data)
        except Exception as e:
            user_text = "(Could not understand)"

        self.response_box.insert(tk.END, f"You: {user_text}\n")
        response = get_ai_response(user_text, self.current_emotion)
        self.response_box.insert(tk.END, f"Therapist: {response}\n\n")
        speak_text(response)

        cursor.execute(
            "INSERT INTO conversations (user_id, question, emotion, answer) VALUES ((SELECT id FROM users WHERE username=?), ?, ?, ?)",
            (self.username, user_text, self.current_emotion, response)
        )
        conn.commit()

        # Clear status label
        self.status_label.config(text="")



    def detect_emotion(self):
        self.current_emotion = detect_facial_emotion()
        speak_text(f"You look {self.current_emotion}")
        self.response_box.insert(tk.END, f"Emotion Detected: {self.current_emotion}\n\n")

    def start_listening(self):
        self.response_box.insert(tk.END, "Listening... Speak now.\n")
        self.status_label.config(text="Recording...")
        speak_text("Listening. Speak now.")
        self.recording = True
        self.audio_chunks = []
        self.listen_thread = threading.Thread(target=self.capture_audio_chunks)
        self.listen_thread.start()

    def capture_audio_chunks(self):
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while self.recording:
                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_chunks.append(audio)
                except sr.WaitTimeoutError:
                    continue  # Keep waiting for audio





    def end_conversation(self):
        speak_text("Bye. Click Take Therapy again to start fresh.")
        self.create_main_menu()

    def view_history(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f4f6f8")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Previous Sessions", font=("Helvetica", 20, "bold"),
                bg="#f4f6f8", fg="#2c3e50").pack(pady=10)

        # Scrollable canvas
        canvas = tk.Canvas(frame, bg="#f4f6f8", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f4f6f8")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === Use 'conversations' table ===
        cursor.execute("""
            SELECT timestamp, emotion, question, answer FROM conversations 
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
            ORDER BY timestamp DESC
        """, (self.username,))
        sessions = cursor.fetchall()

        if not sessions:
            tk.Label(scroll_frame, text="No conversations found.",
                    font=("Helvetica", 14), bg="#f4f6f8", fg="gray").pack(pady=20)
        else:
            for timestamp, emotion, question, answer in sessions:
                session_frame = tk.LabelFrame(scroll_frame, text=f"Time: {timestamp} | Emotion: {emotion}",
                                            font=("Helvetica", 12, "bold"),
                                            padx=10, pady=10, bg="#ffffff", fg="#2c3e50",
                                            bd=2, relief="groove", labelanchor="n")
                session_frame.pack(fill="both", expand=True, padx=20, pady=10)

                convo_box = tk.Text(session_frame, wrap="word", font=("Helvetica", 12),
                                    bg="#f8f9fa", fg="#333333", height=5, width=80)
                convo_box.insert("1.0", f"You: {question}\nTherapist: {answer}")
                convo_box.config(state="disabled")
                convo_box.pack(fill="both", expand=True)

        # Return button
        tk.Button(frame, text="Return", font=("Helvetica", 12),
                bg="#2c3e50", fg="white", command=self.create_main_menu).pack(pady=10)




# === LAUNCH ===
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("800x600")
    app = SoulSyncApp(root)
    root.mainloop()
