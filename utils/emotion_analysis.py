from transformers import pipeline
import torch
from datetime import datetime as dt
import pandas as pd
from datetime import datetime as dt


basic_emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1,truncation=True)
extra_emotion_model = pipeline("text-classification", model="joeddav/distilbert-base-uncased-go-emotions-student", top_k=1,truncation=True)

def is_valid_message(txt):
    if not txt or not isinstance(txt,str) or txt=='Waiting for this message':
        return False
    words =txt.strip().split()
    if len(words) < 4 :
        return False
    junk_words = ["ok", "okay", "hmm", "yes", "no", "huh", "yeah", "uh", "nah", "huh", "uhh", "umm"]
    return not all(word.lower() in junk_words for word in words)

def clean_group_message(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp'])
    df['Valid'] = df['Message'].apply(is_valid_message)
    filtered_df = df[df['Valid']]
    df['date_only'] = df['Timestamp'].dt.date
    grouped = df.groupby(['Sender','date_only'])['Message'].apply(lambda x: " ".join(x)).reset_index()
    return grouped
    
def get_emotions(message):
    basic_result = basic_emotion_model(message)[0][0]
    extra_result = extra_emotion_model(message)[0][0]
    return basic_result['label'], round(basic_result['score'], 2), extra_result['label'], round(extra_result['score'], 2)

def analysed_emotion(grouped_df):
    grouped_df[['Basic Emotion state', 'Basic Emotion Score', 'Specific Emotion state', 'Specific Emotion Score']] = \
        grouped_df['Message'].apply(lambda x: pd.Series(get_emotions(x)))
    grouped_df.drop("Message", axis=1, inplace=True)
    return grouped_df

