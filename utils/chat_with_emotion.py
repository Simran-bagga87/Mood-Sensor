import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from transformers import pipeline

emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
def respond_to_input():
    st.markdown("Pour your heart out with mood sensor")

    llm = ChatGroq(
        temperature=0,
        groq_api_key="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",  # Make sure to replace this
        model_name="llama-3.3-70b-versatile"
    )

    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = ConversationBufferMemory()
        st.session_state.chatbot = ConversationChain(llm=llm, memory=st.session_state.chat_memory)

    user_input = st.text_area("You:", key="user_question", height=100)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def detect_emotion(text):
        emotions = emotion_model(text)
        top_emotion = max(emotions, key=lambda x: x['score'])
        return top_emotion['label'], top_emotion['score']

    if user_input:
        with st.spinner("Analysing your feeling❤️..."):
            # Detect emotion of the user's input
            detected_emotion, emotion_score = detect_emotion(user_input)

            # Constructing short and natural response based on emotion
            if detected_emotion in ["Joy", "Happiness", "Love", "Pride"]:
                response = f"That's awesome! Positive vibes can really lift your mood. What are you most excited about tomorrow?"
            else:
                response = st.session_state.chatbot.run(user_input)

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", response))
            st.session_state.chat_history.append(("Detected Emotion", f"{detected_emotion}: {emotion_score:.2f}"))

    # Show conversation
    for role, message in st.session_state.chat_history:
        if role == "Detected Emotion":
            st.markdown(f"**Emotion Detected:** {message}")
        else:
            st.markdown(f"**{role}:** {message}")

    # Clear chat option
    if st.button("🗑️ Clear chat"):
        st.session_state.chat_history = []
        st.session_state.chat_memory.clear()
