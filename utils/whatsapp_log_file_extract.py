
import re
from datetime import datetime
import pandas as pd

def whatsapp_text(file_b):
    file = file_b.read().decode('utf-8')
    lines =file.split("\n")
    lines = [line.replace('\u202f', ' ').strip() for line in lines if line.strip()]  
    messages = []
    for line in lines:
        match = re.match(r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\s([APap][Mm]) - (.*?): (.+)', line)
        if match:
            date_str,time_str,period,sender,message = match.groups()
            time_str = f"{time_str} {period}"
            dt_str = f"{date_str} {time_str}"
            
            try:
                timestamp = datetime.strptime(dt_str,"%m/%d/%y %I:%M %p")
            except Exception as e:
                print(f"error parsing data: {e}")
                continue
            messages.append((timestamp,sender.strip(),message.strip()))
    if messages:
        df = pd.DataFrame(messages,columns=['Timestamp',"Sender","Message"])
        df = df[df['Message'] != 'Waiting for this message']
        df=df[df['Message']!='<Media omitted>']
        user = df['Sender'].unique()
        return user,df
    else:
        return None
      

    