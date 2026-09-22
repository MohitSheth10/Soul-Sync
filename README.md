# Emotion Counsellor Robot

An AI-powered emotional support robot built for the World Robot Olympiad (Future Innovators). It recognizes who you are, reads how you're feeling, and talks it through with you. The goal is to offer support to teens and young adults, where depression rates have been rising.

## 👥 Team

I led a 3-person team and wrote the software (800+ lines of Python).

- Mohit Sheth: coder and team lead
- Harsh S Dungrani: designer
- Parsen Gonsalves: builder and hardware lead

## 🔍 Features

- 🧑 Custom face recognition model (built under a mentor's guidance) to register new users and recognize returning ones
- 😊 Machine learning emotion detection from the webcam, in real time
- 💬 Conversational AI that responds based on your detected emotion, what you're saying right now, and your past conversations (note: responses can run long — trimming this down is a work in progress)
- 🌈 Changes the surrounding colors to match the detected emotion
- 🎤 Voice input to confirm the user's name via microphone
- 🖼️ Tkinter GUI for capturing face images and displaying the conversation
- 🔁 Automatically updates and saves new face data, stored locally
- 🖨️ Full body is 3D printed and designed by the team

## How it works

1. The webcam captures your face and matches it against stored face data, or registers you as a new user if you're not recognized.
2. Voice input confirms your name.
3. The emotion model reads your current emotional state from your expression.
4. The surrounding colors shift to suit that emotion.
5. The robot starts a conversation using your emotion, your live input, and your stored history — offering support, asking questions, or just talking through how you're feeling.
6. All of this runs through a Tkinter GUI, which handles the face capture and displays the chat.

---

## 🤖 World Robot Olympiad (WRO)

<img width="360" height="480" alt="WhatsApp Image 2026-08-07 at 11 14 55 AM" src="https://github.com/user-attachments/assets/2f7c8fe5-b3fc-4dde-a5d4-943267378b97" />

This started as my WRO project. After the competition, the organizers invited me back to join the event coordination team. I worked with fellow team members to organize and run the event, and collaborated with judges to evaluate 42 of the participating teams, helping troubleshoot issues for participants along the way.

I also gave the WRO closing speech. The judges liked my input enough that the next day I was asked to shadow-judge 12 projects — giving feedback to the judges and learning a lot about how projects are actually graded. I discussed projects with several judges and sat in on the final meeting where the 6 teams qualifying for nationals were decided.

**Favorite idea:** Rangoli Maker (execution was rough, but the idea was strong) — won 2nd place.

**Favorite execution:** The String Theory — a robotic puppet show where motors control multiple strings to make puppets act out a play, synced to music. It tackles a real problem too: younger generations losing interest in traditional puppetry. - Won 1st place
