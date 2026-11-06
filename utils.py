
# utils.py
import time
import requests
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
import os
from pathlib import Path
from project_paths import TRANSCRIPTIONS_CSV, RECORDING_DIR, VOICE_AUDIO_DIR




# Set the custom directory for storing audio files
AUDIO_SAVE_DIR = str(VOICE_AUDIO_DIR)
record = str(RECORDING_DIR)

def _load_api_key():
    """Read the key from environment or Streamlit secrets without crashing imports."""
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("secrets", {}).get("API_KEY") or st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None

api_key = _load_api_key()
client = Groq(api_key=api_key) if api_key else None
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=api_key, max_tokens=500) if api_key else None


def audio_bytes_to_wav(audio_bytes):
    try:
        print(f"Audio bytes size: {len(audio_bytes)} bytes")
        
        # Define the path for saving the WAV file
        wav_file_path = os.path.join(AUDIO_SAVE_DIR, "user_input.wav")
        
        # Load the audio from bytes into an AudioSegment object
        audio = AudioSegment.from_file(BytesIO(audio_bytes))
        
        # Optionally, print information about the audio
        print(f"Audio duration: {audio.duration_seconds} seconds")
        
        # Convert the audio to mono (1 channel) and set a sample rate of 16000 Hz
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Export the audio as a WAV file
        audio.export(wav_file_path, format="wav")
        print(f"WAV file saved at: {wav_file_path}")
        
        return wav_file_path 
    except Exception as e:
        print(f"Error during WAV file conversion: {e}")
        return None
    

def split_audio(file_path, chunk_length_ms):
    audio = AudioSegment.from_wav(file_path)
    return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
import csv
CSV_SAVE_PATH = str(TRANSCRIPTIONS_CSV)

def save_transcription_to_csv(transcription):
    """
    Append the transcription to a CSV file.
    Args:
        transcription (str): The transcription text to be saved.
    """
    try:
        # Check if the file exists to decide whether to append or create new
        file_mode = 'a' if os.path.exists(CSV_SAVE_PATH) else 'w'
        
        with open(CSV_SAVE_PATH, mode=file_mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # If writing to a new file, write the header
            if file_mode == 'w':
                
                writer.writerow(["message"])  # Header for the CSV file
            
            # Append the transcription to the CSV file
            
            writer.writerow([transcription])
        print(f"Transcription saved to {CSV_SAVE_PATH}")
    
    except Exception as e:
        print(f"Error while saving transcription to CSV: {e}")
        st.error(f"Error while saving transcription to CSV: {e}")

def speech_to_text(audio_bytes):
    try:
        # Convert the audio bytes to WAV
        if client is None:
            st.error("Groq API key is not configured. Set GROQ_API_KEY or configure .streamlit/secrets.toml.")
            return "Error"
        temp_wav_path = audio_bytes_to_wav(audio_bytes)

        if temp_wav_path is None:
            return "Error"

        # Increase file size limit
        if os.path.getsize(temp_wav_path) > 50 * 1024 * 1024:
            st.error("File size exceeds the 50 MB limit. Please upload a smaller file.")
            return "Error"

        # Define chunk length (e.g., 5 minutes = 5 * 60 * 1000 milliseconds)
        chunk_length_ms = 5 * 60 * 1000
        chunks = split_audio(temp_wav_path, chunk_length_ms)

        transcription = ""
        for chunk in chunks:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk:
                chunk.export(temp_chunk.name, format="wav")
                with open(temp_chunk.name, "rb") as file:
                    # Create transcription from audio chunk
                    chunk_transcription = client.audio.transcriptions.create(
                        file=("audio.wav", file.read()),
                        model="whisper-large-v3",
                        response_format="text",
                        language="en",
                        temperature=0.0,
                    )
                    transcription += chunk_transcription + " "
                    print(f"Transcription for chunk: {chunk_transcription}")

        # After processing all chunks, save the transcription to the CSV
        # Clean up the transcription (remove duplicate lines)
        transcription_lines = transcription.split('\n')
        unique_lines = list(dict.fromkeys(transcription_lines))  # Remove duplicates while preserving order
        cleaned_transcription = '\n'.join(unique_lines)

        # Save the final transcription to CSV
        save_transcription_to_csv(cleaned_transcription)

        return cleaned_transcription.strip()
    
    except Exception as e:
        st.error(f"Error during speech-to-text conversion: {e}")
        print(f"Error during speech-to-text conversion: {e}")
        return "Error"

def text_to_speech(text, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            # Enforce English language for text-to-speech
            tts = gTTS(text=text, lang='en')
            
            # Define the path for saving the audio file
            audio_file_path = os.path.join(record, "response_audio.mp3")
            
            # Save the TTS audio to the specified directory
            tts.save(audio_file_path)
            audio = AudioSegment.from_mp3(audio_file_path)
            return audio
        except requests.ConnectionError as e:
            attempt += 1
            if attempt < retries:
                st.warning(f"Internet connection issue. Retrying ({attempt}/{retries})...")
                time.sleep(delay)  # Wait before retrying
            else:
                st.error(f"Failed to connect after {retries} attempts. Please check your internet connection.")
                # Return silent audio in case of error
                return AudioSegment.silent(duration=1000)
        except Exception as e:
            st.error(f"Error during text-to-speech conversion Please check your internet connection: {e}")
            # Return silent audio in case of other errors
            return AudioSegment.silent(duration=1000)

def remove_punctuation(text):
    # Remove punctuation from the text
    return re.sub(r'[^\w\s]', '', text)

def get_llm_response(query, chat_history):
    try:
        if llm is None:
            st.error("Groq API key is not configured. Set GROQ_API_KEY or configure .streamlit/secrets.toml.")
            return "The voice assistant is not configured yet. Please contact the application administrator."
        # Updated template with detailed guidelines
        template = """
               You are a highly qualified female psychiatrist assistant chatbot named "psychologist
               " with extensive experience in mental health. Your role is to provide professional, empathetic, and culturally authentic advice and answers to the user's questions. You communicate using everyday language, incorporating local idioms and expressions while avoiding loanwords from other languages.

                Your expertise is exclusively in providing information and advice related to mental health. If a question falls outside the scope of mental health, you should respond with, "I specialize only in mental health-related queries."

                Key Considerations:

                Professionalism: Maintain a high level of expertise and ethical standards.
                Cultural Authenticity: Understand and reflect the values, beliefs, and customs relevant to the user’s cultural context.
                Empathy: Show genuine compassion and support for the user's emotional well-being.
                You do not provide information outside of this 
                  scope. If a question is not about psychologist,mental health, respond with,
                 "I specialize only in psychologist,mental health related queries."                 
                 **Chat History:** {chat_history}

                **User:** {user_query}

        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()

        response_gen = chain.stream({
            "chat_history": chat_history,
            "user_query": query
        })

        # Combine all parts of the response and apply text clean-up
        response_text = ''.join(list(response_gen))
        response_text = remove_punctuation(response_text)

        # Remove repeated text
        response_lines = response_text.split('\n')
        unique_lines = list(dict.fromkeys(response_lines))  # Remove duplicates while preserving order
        cleaned_response = '\n'.join(unique_lines)

        return cleaned_response
    except Exception as e:
        st.error(f"Error during LLM response generation: {e}")
        return "Error"
    
    
def create_welcome_message():
    welcome_text = "Hello, I'm your Mindx wellness assistant. How can I help you?"
    welcome_audio_path = os.path.join(record, "welcome_message.mp3")
    try:
        tts = gTTS(text=welcome_text, lang='en')
        tts.save(welcome_audio_path)
        return welcome_audio_path
    except Exception as exc:
        st.warning(f"Could not generate welcome audio: {exc}")
        return None


