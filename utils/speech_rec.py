import speech_recognition as sr
from transformers import pipeline
import datetime
import sqlite3
import os

emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1,truncation=True)
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.record(source, duration=15)  
        try:
            text = r.recognize_google(audio)
            print("Transcribed:", text)
            return text
        except sr.UnknownValueError:
            return "Could not understand what you said"
        except sr.RequestError as e:
            return f"Error from Google API: {e}"


def analyse_emotion(text):
    result = emotion_model(text)[0][0]['label']
    return result

def save_journal(username,text,emotion):
    conn = sqlite3.connect("Mood_Sense.db")
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p")
    c.execute(''' INSERT INTO JOURNAL
              (NAME,ENTRY,EMOTION,DATE) VALUES
              (?,?,?,?)''',(username,text,emotion,date))
    conn.commit()
    conn.close()
        