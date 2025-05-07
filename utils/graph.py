import streamlit as st
import plotly.express as px
import sqlite3
import pandas as pd

def show_emotion_dashboard(grouped_df):
    st.subheader(f"📈 Mood Dashboard for {st.session_state['selected_user']}")

    fig1 = px.bar(grouped_df, 
                  x='date_only', 
                  y='Basic Emotion Score',
                  color='Basic Emotion state',
                  title='📊 Daily Basic Emotion Scores',
                  labels={'date_only': 'Date'},
                  hover_data=['Basic Emotion state'])

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(grouped_df,
                   x='date_only',
                   y='Specific Emotion Score',
                   color='Specific Emotion state',
                   title='📉 Specific Emotion Trends Over Time',
                   markers=True)

    st.plotly_chart(fig2, use_container_width=True)

    pie_df = grouped_df['Specific Emotion state'].value_counts().reset_index()
    pie_df.columns = ['Emotion', 'Count']

    fig3 = px.pie(pie_df, 
                  names='Emotion', 
                  values='Count',
                  title='🥧 Specific Emotion Distribution',
                  hole=0.4)

    st.plotly_chart(fig3, use_container_width=True)

def show_emotion_dashboard_for_journal():
    conn =sqlite3.connect('Mood_Sense.db')
    user = st.session_state['username']
    c =conn.cursor()
    query = '''
              SELECT * FROM JOURNAL
              WHERE NAME= ?'''
    df = pd.read_sql_query(query,conn,params = (user,))
    
    df['DATE'] = pd.to_datetime(df['DATE'])
    st.subheader(f"📈 Mood Dashboard for {user}")
    fig1 = px.bar(df, x=df['DATE'].dt.time,
                  y='EMOTION',
                  color='EMOTION',
                  title='📊 Daily Basic Emotion Scores')
    st.plotly_chart(fig1, use_container_width=True)
    
