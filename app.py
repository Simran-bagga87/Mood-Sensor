import streamlit as st
import sqlite3
import bcrypt
from utils.whatsapp_log_file_extract import whatsapp_text
from utils.emotion_analysis import analysed_emotion,clean_group_message
from utils.speech_rec import recognize_speech,analyse_emotion,save_journal
from utils.chat_with_emotion import respond_to_input
from utils.graph import show_emotion_dashboard,show_emotion_dashboard_for_journal
# for connection
def connect_db():
    return sqlite3.connect('Mood_Sense.db')

def check_password(password):
        sc = "!@#$%^&*(),.?\":{}|<>"
        has_lower = False
        has_upper = False
        has_sc = False
        has_digit = False
        has_length = False
        if len(password) >=8:
            has_length = True
        for char in password:
            if char.isdigit():
                has_digit=True
            if char.islower():
                has_lower=True
            if char.isupper():
                has_upper=True
            if char in sc:
                has_sc = True
        if has_length and has_lower and has_digit and has_sc and has_upper :
            return True
        else:
            return False
        

# Signup function
def signup(USERNAME,PASSWORD):
    st.markdown("""
    <style>
        .error {
            color: #e7cac1;
            font-size: 14px;
            background-color: rgba(0, 0, 0, 0.5); 
            
        }
    </style>
""", unsafe_allow_html=True)
    conn = connect_db()
    c = conn.cursor()
    if check_password(PASSWORD):
        hashed_password = bcrypt.hashpw(PASSWORD.encode('utf-8'),bcrypt.gensalt())
        
        
        c.execute('''INSERT INTO USERS 
                    (USERNAME,PASSWORD) VALUES (?,?)''',(USERNAME,hashed_password))
            
        conn.commit()
        conn.close()
        return True
    else:
        st.markdown('<p class="error">Please enter a valid password that includes at least one special character from !@#$%^&*(),.?":{}|<>, one uppercase letter, one lowercase letter, one digit, and is at least 8 characters long.</p.',unsafe_allow_html=True)
        return False
    

# Login Function  
def login(USERNAME,PASSWORD):
    conn = connect_db()
    c = conn.cursor()

    c.execute('''SELECT PASSWORD 
              FROM USERS
              WHERE USERNAME = ?''',(USERNAME,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(PASSWORD.encode('utf-8'),result[0]):
        return True
    return False

# Authorization Function
def auth():
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://wallpapers.com/images/high/emotions-background-tolibu330h6pg9it.webp");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stTextInput, .stPasswordInput, .stSelectbox {{
        max-width: 300px;
        margin: 0 auto;
    }}

    .stButton {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }}
    .stButton > button {{
        background-color: #FF5722; 
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        transition: 0.3s ease;
        width: 100%;
        max-width: 300px;
    }}
    .st-success {{
        color: #4CAF50;
        font-size: 16px;
        font-weight: bold;
    }}

    .stButton > button:hover {{
        background-color: black; 
        color:white;
        transform: scale(1.03);
    }}

    .stTextInput input, .stPasswordInput input, .stSelectbox select {{
        color: black !important; 
    }}

    input {{
        background-color: rgba(255, 255, 255, 0.85) !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

    st.markdown('<h1 style="text-align: center; font-size: 36px; color: white;">MOOD SENSE - Login/Signup</h1>', unsafe_allow_html=True)

    choice = st.selectbox("select an option ",['Login','Signup'])
    if choice == 'Signup':
        Username = st.text_input('Enter your username')
        password = st.text_input("enter your password",type="password")
        if st.button("SignUp"):
            if signup(Username,password):
                st.success("your account is created,you can log in now")

    elif choice=="Login":
        Username = st.text_input('Enter your username')
        password = st.text_input("enter your password",type="password")
        if st.button("Login"):
            if login(Username,password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = Username
                st.success("Login Successfully")
            else:
                st.error("Invalid Credentials")

def upload_page():
    
    st.markdown("""
        <style>
        .header {
                font-size: 40px;
                text-align: center;
                color: white;
                font-weight: bold;
                }
        .stWrite {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            color: white;
            background-color: rgba(0, 0, 0, 0.5); /* 50% transparency */
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='header'>Upload Whatsapp Chat </p>", unsafe_allow_html=True)
    file = st.file_uploader("Upload Your Whatapp Log file (txt) here \n : first go to chat select upper right three dots and export chat ", type=['txt'])
    
    if file:
        user, df = whatsapp_text(file)
        st.session_state['user_chat'] = user
        st.session_state['chat_df'] = df
        st.success("Chat imported. Now go to 'Analyse Emotion'.")
    
    st.markdown("<p class='stWrite'>Your chats are not stored in our database. It's deleted automatically after feeding to the model.</p>", unsafe_allow_html=True)

def analyse_page():
    st.subheader("Analyse Emotion")
    if "chat_df" not in st.session_state:
        st.warning("Please Upload chat first")
        return
    df = st.session_state['chat_df']
    user = st.session_state['user_chat']
    user=  ["Select a user"] + list(user)

    choice = st.radio("Select user", user, index=0)
    if choice != "Select a user":
        if st.button("Analyse Emotion"):
            df = df[df['Sender']==choice]
            with st.spinner("Processing..."):
                cleaned_grouped_data = clean_group_message(df)
                if cleaned_grouped_data.empty:
                    st.warning("No valid message found")
                else:
                    analysed_emotion_data = analysed_emotion(cleaned_grouped_data)
                    st.session_state['selected_user'] = choice
                    conn = connect_db()
                    analysed_emotion_data.to_sql(f"whatsapp_logs_grouped_{choice}", conn, if_exists="append", index=False)
                    conn.close()
                    st.success("Results saved.")
                    show_emotion_dashboard(analysed_emotion_data)
                    st.download_button("Download Emotion Report", analysed_emotion_data.to_csv(index=False), "report.csv", "text/csv")


def audio_rec():
    st.markdown("Speak for 20 seconds")
    if st.button("Record Voice Joural"):
        with st.spinner("Listening..."):
            text = recognize_speech()
            if text and text!="Could not understand what u said":
                st.success(f"Transcribed:{text}")
                emotion = analyse_emotion(text)
                st.info(f"Detected Emotion:{emotion}")
                
                save_journal(st.session_state['username'],text,emotion)
            else:
                st.error("Could not understand your voice.Try Again")
    df = show_emotion_dashboard_for_journal()
    st.write(df)



        



def main():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/angry-reactions-with-empty-space-background_79603-1025.jpg?t=st=1745248097~exp=1745251697~hmac=9e075f0060c3ab639e5867e62cfb1600b843a6819cd7ddf339864b9e2fb23d86&w=1380");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        
        }}
        
        
        </style>
        """,
        unsafe_allow_html=True
    )
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if not  st.session_state['logged_in']:
        auth()
    else:
        st.sidebar.title(f"Welcome,{st.session_state['username'].capitalize()}, Let's reflect your emotion today.")
        
        page = st.sidebar.radio("Select from below",["Upload Chat","Analyse Emotion","Speech Journal","Chat heart-to-heart","Log Out"])
        if page == "Upload Chat":
            upload_page()
        elif page =="Analyse Emotion":
            analyse_page()
        elif page =="Speech Journal":
            audio_rec()
        elif page =="Chat heart-to-heart":
            respond_to_input()
        elif page == "Log Out":
            st.session_state['logged_in']=False   
    
if __name__ == "__main__":
    main()







