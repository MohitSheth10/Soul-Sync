# Soul Sync: an Emotion Counselor Robot

A robot that recognizes who you are, reads how you're feeling from your face, and holds a supportive conversation shaped by your emotion, what you say, and what you've said before. Built for the World Robot Olympiad (Future Innovators), where it won **silver in the online round** and **bronze at regionals**. It's aimed at teens and young adults, where depression rates have been rising.

## 👥 Team

I led a team of 3 and wrote the software (800+ lines of Python). My 2 other teammates designed the robot and built the hardware.

- Mohit Sheth: coder and team lead
- Teammate: designer
- Teammate: builder and hardware lead

## 🏅 Results

- WRO Future Innovators: silver, online round
- WRO Future Innovators: bronze, regionals

## 🔍 Features

- 🧑 Custom face recognition model (built under a mentor's guidance) to register new users and recognize returning ones
- 😊 Machine learning emotion detection from the webcam, in real time
- 💬 Conversational AI that responds based on your detected emotion, what you're saying right now, and your past conversations
- 🌈 Changes the surrounding colors to match the detected emotion
- 🎤 Voice input to confirm the user's name via microphone
- 🖼️ Tkinter GUI for capturing face images and displaying the conversation
- 🔁 Automatically updates and saves new face data and conversation history, stored locally
- 🖨️ Full body is 3D printed and designed by the team

## How it works

1. The webcam captures your face and matches it against stored face data, or registers you as a new user if you're not recognized.
2. Voice input confirms your name.
3. The emotion model reads your current emotional state from your expression.
4. The surrounding colors shift to suit that emotion.
5. The robot starts a conversation using your emotion, your live input, and your stored history, offering support, asking questions, or just talking through how you're feeling.
6. All of this runs through a Tkinter GUI, which handles the face capture and displays the chat.

## 🛠 Built With

Python, OpenCV (face recognition), Keras (emotion detection), Cohere (conversational AI), SQLite (conversation history), Tkinter (interface), SpeechRecognition and pyttsx3 (voice in and out).

## ▶️ How to Run

1. Install Python 3 and the libraries: `pip install opencv-contrib-python numpy keras tensorflow cohere pyttsx3 SpeechRecognition pyaudio keyboard pyserial pillow`
2. Set your own Cohere API key as the `COHERE_API_KEY` environment variable.
3. Add the trained emotion model file (`emotion_detection_model.h5`) and update its path in `CurrentFinalEmotionBot.py`. The path is currently set to a folder on my Windows computer.
4. Run `python CurrentFinalEmotionBot.py`. This is the main app.

`FinalFaceBot(voice_input).py` is a separate program that handles face registration and voice name confirmation.

## ⚠️ Known Limitations

- Responses can run long. Trimming them is a work in progress.
- The emotion model file is not included in this repo.
- Conversation needs an internet connection and a Cohere API key.

---

## 🤖 World Robot Olympiad (WRO) involvement

<img width="360" height="480" alt="Mohit at the World Robot Olympiad" src="https://github.com/user-attachments/assets/2f7c8fe5-b3fc-4dde-a5d4-943267378b97" />

This started as my WRO project. After the competition, the organizers invited me back to join the event coordination team. I worked with fellow team members to organize and run the event, and collaborated with judges to evaluate 42 of the participating teams, helping troubleshoot issues for participants along the way.

I also gave the WRO closing speech. The judges liked my input enough that the next day I was asked to shadow-judge 12 projects, giving feedback to the judges and learning a lot about how projects are actually graded. I discussed projects with several judges and sat in on the final meeting where the 6 teams qualifying for nationals were decided.
