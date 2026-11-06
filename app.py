import tempfile
import re
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
st.set_page_config(page_title='Audio-based Chatbot')
from audio_recorder_streamlit import audio_recorder
from utils import audio_bytes_to_wav, speech_to_text, text_to_speech, get_llm_response, create_welcome_message
import re
import zipfile
import os
import subprocess
from pathlib import Path
from project_paths import TRANSCRIPTIONS_CSV, VOICE_AUDIO_DIR, CONVERSATION_DIR, BASE_DIR
from auth import require_auth




AUDIO_SAVE_DIR = str(VOICE_AUDIO_DIR)

# Ensure the directory exists, create it if it doesn't
if not os.path.exists(AUDIO_SAVE_DIR):
    os.makedirs(AUDIO_SAVE_DIR)

covoo = str(CONVERSATION_DIR)
os.makedirs(covoo, exist_ok=True)

def create_audio_zip(audio_files):
    """Create a zip file containing all the audio files in the specified location."""
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, audio_file in enumerate(audio_files):
            # Save audio to the specified location
            if audio_file and os.path.isfile(audio_file):
                audio_path = os.path.join(covoo, f"conversation_{i+1}.mp3")
                zipf.write(audio_file, arcname=os.path.basename(audio_path))
    zip_io.seek(0)
    return zip_io


def truncate_csv():
    file_path = TRANSCRIPTIONS_CSV
    if os.path.exists(file_path):
        os.remove(file_path)



def main():

    st.markdown("<h1 style='color: black;'>🎤 Mindx 🤖</h1>", unsafe_allow_html=True)

    st.sidebar.markdown("""
    <h1 style='color: black; font-size: 40px; font-weight: bold; text-align: center;
              background-color: #f0f0f0; padding: 20px; border-radius: 10px;'>
        Welcome
    </h1>
""", unsafe_allow_html=True)
    sidebar_image = BASE_DIR / '200w.gif'
    if sidebar_image.exists():
        st.sidebar.image(str(sidebar_image), width=250)
    else:
        st.sidebar.caption('Mindx wellness assistant')

    # Initialize chat history if not already present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []

    if "played_audios" not in st.session_state:
        st.session_state.played_audios = {}  # To track if an audio file has been played

    # Handle the initial chat history setup
    if len(st.session_state.chat_history) == 0:
        welcome_audio_path = create_welcome_message()
        st.session_state.chat_history = [
            AIMessage(content="Hello, I'm your mindx assistant. How can I help you?", audio_file=welcome_audio_path)
        ]
        if welcome_audio_path:
            st.session_state.played_audios[welcome_audio_path] = False

    # Sidebar with mic button on top
    with st.sidebar:
        # Show "Speaking..." message during recording
        audio_bytes = audio_recorder(
            energy_threshold=0.01,
            pause_threshold=0.8,
            text="Speak now...max 5 min",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x"  # Adjust the icon size
        )
        st.info("")  # Clear the "Speaking..." message after recording

        if audio_bytes:
            # Save the user input audio file
            temp_audio_path = audio_bytes_to_wav(audio_bytes)
            if temp_audio_path:
                # Transcribe the audio and update chat history
                user_input = speech_to_text(audio_bytes)
                st.session_state.chat_history.append(HumanMessage(content=user_input, audio_file=temp_audio_path))

                # Generate AI response
                response = get_llm_response(user_input, st.session_state.chat_history)

                # Convert the response to audio
                audio_response = text_to_speech(response)

                # Create an in-memory BytesIO stream
                audio_stream = BytesIO()
                audio_response.export(audio_stream, format="mp3")
                audio_stream.seek(0)  # Rewind the stream to the beginning

                # Save the AI response audio file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_response:
                    audio_stream.seek(0)
                    temp_audio_response.write(audio_stream.read())
                    audio_response_file_path = temp_audio_response.name

                # Append AI response text and audio to history
                st.session_state.chat_history.append(AIMessage(content=response, audio_file=audio_response_file_path))
                st.session_state.played_audios[audio_response_file_path] = False  # Mark the new response as not played




        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        with col1:
            if st.button('Save History'):

                st.success("Chat history saved!")

        with col2:
            if st.button("New Chat"):
            # Save the current chat history to the chat_histories list
                st.session_state.chat_histories.append(st.session_state.chat_history)
                # Initialize a new chat history with the default welcome message
                welcome_audio_path = create_welcome_message()
                st.session_state.chat_history = [
                    AIMessage(content="Hello, I'm your mindx  assistant. How can I help you?", audio_file=welcome_audio_path)
                ]
                if welcome_audio_path:
                    st.session_state.played_audios[welcome_audio_path] = False

        # Place buttons for navigation in the grid
        with col3:
            if st.button('Go to Login Page'):
                st.info('Open the frontend login page in your browser. Authentication is not implemented by this prototype.')

        with col4:
            if st.button('Go to Routine'):
                 # Save the current chat history to the chat_histories list before ending
                st.session_state.chat_histories.append(st.session_state.chat_history)
                # Clear the chat history
                st.session_state.chat_history = []
                st.session_state.played_audios = {}

                # Start the yoga app in a different port using subprocess
                import random

# Generate a random port to avoid clashes and open a new page each time
                port = random.randint(8610, 8700)  # choose a port within a range
                subprocess.Popen(["streamlit", "run", "sentimet.py", "--server.port", str(port)])

                st.success("Navigating to Yoga Routine...")

        if st.session_state.chat_histories:
            st.subheader("Chat History")
            for i, hist in enumerate(st.session_state.chat_histories):
                if st.button(f"Chat {i + 1}", key=f"chat_{i}"):
                    st.session_state.chat_history = hist



    # Display the conversation history in the main area
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(f"**AI:** {message.content}")
                # Check if the audio file has already been played
                if getattr(message, 'audio_file', None):
                    if not st.session_state.played_audios.get(message.audio_file, False):
                        st.audio(message.audio_file, format="audio/mp3", autoplay=True)
                        st.session_state.played_audios[message.audio_file] = True  # Mark as played
                    else:
                        st.audio(message.audio_file, format="audio/mp3", autoplay=False)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                if getattr(message, 'audio_file', None):
                    st.audio(message.audio_file, format="audio/wav", autoplay=False)

      # Button to download the entire conversation as a zip file
    if st.button("Download Conversation as Audio"):
        audio_files = [msg.audio_file for msg in st.session_state.chat_history if hasattr(msg, 'audio_file')]
        if audio_files:
            zip_io = create_audio_zip(audio_files)
            st.download_button(
                label="Download Audio Files",
                data=zip_io,
                file_name="conversation_audio.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    if require_auth():
        main()
