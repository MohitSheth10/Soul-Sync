# Emotion Counsellor Robot

An AI-powered emotional support robot that detects your emotions through webcam-based face recognition, holds a conversation with you about how you're feeling, and responds through a Tkinter-based GUI. It also remembers registered users and confirms identity through voice input.

## 🔍 Features

- 😊 Detects user emotion in real time via webcam
- 💬 Chats with the user based on detected emotion (note: responses can run long — trimming this down is a work in progress)
- 🧠 Remembers faces using a JSON-based encoding system
- 🎤 Voice input for user name confirmation via microphone
- 🖼️ Tkinter GUI for capturing face images and displaying the conversation
- 🔁 Automatically updates and saves new face data
- 📁 Stores face images locally for easy management

## How it works

1. The webcam captures the user's face and matches it against stored face encodings, or registers a new user if unrecognized.
2. Voice input confirms the user's name.
3. The system detects the user's current emotional state from their expression.
4. Based on the detected emotion, the robot starts a conversation — offering support, asking questions, or just talking through how the user is feeling.
5. All of this runs through a Tkinter GUI, which handles the face capture and displays the chat.

---

## 🤖 World Robot Olympiad (WRO)

![WRO robot](assets/wro-robot.jpg)

This started as my WRO project. After the competition, the organizers invited me back to join the event coordination team. I worked with fellow team members to organize and run the event, and collaborated with judges to evaluate 42 of the participating teams, helping troubleshoot issues for participants along the way.

I also gave the WRO closing speech. The judges liked my input enough that the next day I was asked to shadow-judge 12 projects — giving feedback to the judges and learning a lot about how projects are actually graded. I discussed projects with several judges and sat in on the final meeting where the 6 teams qualifying for nationals were decided.

**Favorite idea:** Rangoli Maker (execution was rough, but the idea was strong) — won 2nd place.

**Favorite execution:** The String Theory — a robotic puppet show where motors control multiple strings to make puppets act out a play, synced to music. It tackles a real problem too: younger generations losing interest in traditional puppetry. - Won 1st place
