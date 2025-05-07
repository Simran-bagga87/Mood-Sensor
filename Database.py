import sqlite3

# table for user

def create_db():
    conn = sqlite3.connect("Mood_Sense.db")
    c = conn.cursor()
    c.execute(''' CREATE TABLE IF NOT EXISTS USERS 
              ( ID INTEGER PRIMARY KEY AUTOINCREMENT,
              USERNAME TEXT UNIQUE NOT NULL,
              PASSWORD TEXT NOT NULL)''')
    
# table for journal 

    c.execute(''' CREATE TABLE IF NOT EXISTS JOURNAL
              (ID INTEGER PRIMARY KEY AUTOINCREMENT,
               NAME TEXT NOT NULL,
              ENTRY TEXT,
              EMOTION TEXT,
              DATE TEXT,
              FOREIGN KEY(NAME) REFERENCES USERS(USERNAME))''')
    conn.commit()
    conn.close()

create_db()