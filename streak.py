# main.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from threading import Thread, Event
from commands import handle_command
from text_utils import update_text
import cv2
from PIL import Image, ImageTk
import time
import requests
import pyttsx3
import speech_recognition as sr
from decouple import config
from datetime import datetime
from random import choice
from utils import opening_text

USERNAME = config('USER')
BOTNAME = config('BOTNAME')

engine = pyttsx3.init('sapi5')

# Set Rate
engine.setProperty('rate', 190)

# Set Volume
engine.setProperty('volume', 1.0)

# Set Voice (Female)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Use an Event to signal threads to stop
exit_event = Event()

# Text to Speech Conversion
def speak(text):
    """Used to speak whatever text is passed to it"""
    engine.say(text)
    engine.runAndWait()

# Greet the user
def greet_user():
    """Greets the user according to the time"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good Morning {USERNAME}")
    elif 12 <= hour < 16:
        speak(f"Good afternoon {USERNAME}")
    elif 16 <= hour < 19:
        speak(f"Good Evening {USERNAME}")
    speak(f"I am {BOTNAME}. How may I assist you?")

# Takes Input from User
def take_user_input():
    """Takes user input, recognizes it using Speech Recognition module and converts it into text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening....')
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        if not 'exit' in query or 'stop' in query:
            speak(choice(opening_text))
        else:
            hour = datetime.now().hour
            if 21 <= hour < 6:
                speak("Good night sir, take care!")
            else:
                speak('Have a good day sir!')
            exit_event.set()  # Set the event to signal threads to stop
    except KeyboardInterrupt:
        exit_event.set()
    except Exception:
        speak('Sorry, I could not understand. Could you please say that again?')
        query = 'None'
    return query

class VideoPlayer:
    def __init__(self, root, video_source="rcproject.mp4", canvas_width=320, canvas_height=240):
        self.root = root
        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.btn_play = tk.Button(self.root, text="Play", command=self.play_video)
        self.btn_play.pack()

        self.update()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def play_video(self):
        if not self.vid.isOpened():
            self.vid = cv2.VideoCapture(self.video_source)

    def loop_video(self):
        while not exit_event.is_set():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
                photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                self.root.update_idletasks()
                self.root.after(1, lambda: None)  # Process events to keep the window responsive

                # Check if the video has reached the end and rewind to the beginning
                if not ret:
                    self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                # Handle the case when the video capture fails
                print("Error capturing video frame.")
                break

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            # Resize frame to fit within canvas dimensions
            frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.root.after(1, self.update)  # Decreased interval for faster playback

        # Check if the video has reached the end and rewind to the beginning
        if not ret:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def on_closing(self):
        exit_event.set()
        self.root.destroy()

class JarvisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.video_source = "rcproject.mp4"
        self.vid = cv2.VideoCapture(self.video_source)

        self.conversation_history = []

        # Set smaller dimensions for better performance
        self.canvas_width = 320
        self.canvas_height = 240

        self.video_player = VideoPlayer(self.root, video_source=self.video_source, canvas_width=self.canvas_width, canvas_height=self.canvas_height)

        self.output_text = ScrolledText(self.root, wrap=tk.WORD, width=40, height=10)
        self.output_text.pack()

        self.jarvis_thread = Thread(target=self.jarvis_program)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the threads
        self.jarvis_thread.start()

        self.root.mainloop()

    def update_text(self, text):
        update_text(self.output_text, text)

    def jarvis_program(self):
        greet_user()
        while not exit_event.is_set():
            query = take_user_input().lower()

            # Add user query to the conversation history
            self.conversation_history.append(f"You: {query}")
            self.update_text(f"You: {query}")

            response = handle_command(query)

            # Add Jarvis's response to the conversation history
            self.conversation_history.append(f"Jarvis: {response}")
            self.update_text(f"Jarvis: {response}")

    def on_closing(self):
        exit_event.set()
        self.jarvis_thread.join()
        self.root.destroy()

if __name__ == '__main__':
    app = JarvisApp()
