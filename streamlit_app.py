import streamlit as st
import openai
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


# Set up OpenAI API key
st.sidebar.header('OpenAI API Key')
openai.api_key = st.sidebar.text_input('Enter your OpenAI API key:')

# Set up email parameters
from_email = 'your_email@example.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'your_username'
smtp_password = 'your_password'

# Set up Streamlit app UI
st.title('Transcription App')
mp3_file = st.file_uploader('Upload an MP3 file:', type=['mp3'])
email_address = st.text_input('Enter your email address:')
submit_button = st.button('Transcribe and Email')


# Define function to split MP3 file into chunks and transcribe each chunk using OpenAI Whisper
def transcribe_mp3(mp3_file):
    chunk_size = 24 * 1024 * 1024 # 24 MB
    chunks = []
    i = 1
    while True:
        chunk = mp3_file.read(chunk_size)
        if not chunk:
            break
        filename = f'chunk{i}.mp3'
        with open(filename, 'wb') as f:
            f.write(chunk)
        audio_file = open(filename, 'rb')
        transcript = openai.Audio.transcribe('whisper-1', audio_file)
        chunks.append(transcript)
        os.remove(filename)
        i += 1
    return ' '.join(chunks)


# Define function to send email with transcript as attachment
def send_email(from_email, smtp_server, smtp_port, smtp_username, smtp_password, to_email, subject, body, attachment_filename, attachment_content):
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body))
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(attachment_content)
    attachment.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
    message.attach(attachment)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, message.as_bytes())
        

# Define Streamlit app behavior when the submit button is clicked
if submit_button and mp3_file and email_address and openai.api_key:
    try:
        transcript = transcribe_mp3(mp3_file)
        send_email(from_email, smtp_server, smtp_port, smtp_username, smtp_password, email_address, 'Transcription', transcript, 'transcription.txt', transcript.encode('utf-8'))
        st.success('Transcription complete! Check your email for the transcript.')
        transcript_file = open('transcription.txt', 'w')
        transcript_file.write(transcript)
        transcript_file.close()
        with open('transcription.txt', 'rb') as f:
            transcript_content = f.read()
        transcript_link = f'<a href="data:application/octet-stream;base64,{base64.b64encode(transcript_content).decode()}" download="transcription.txt">Download transcript</a>'
        st.markdown(transcript_link, unsafe_allow_html=True)
    except Exception as e:
        st.error(f'Error: {e}')
