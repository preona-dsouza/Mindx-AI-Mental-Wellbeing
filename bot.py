
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO


# Function to process audio and convert it to text
def process_audio(audio_file):
    recognizer = sr.Recognizer()

    # Convert audio file to .wav format (if not already in .wav)
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_frame_rate(16000)  # Standard frame rate for speech recognition
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    # Recognize speech using SpeechRecognition
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {e}"

# Streamlit app interface
def main():
    st.title("AI Chatbot Voice-to-Text")

    # Allow user to upload an audio file
    audio_file = st.file_uploader("Upload a voice message (MP3/WAV)", type=["wav", "mp3", "m4a"])
    
    if audio_file:
        st.audio(audio_file, format="audio/wav")
        
        if st.button("Convert to Text"):
            with st.spinner("Processing audio..."):
                result_text = process_audio(audio_file)
            st.write(result_text)
            st.success("Conversion Complete!")
            st.write("**Transcribed Text:**")
            st.write(result_text)

    # Chatbot interface
    st.subheader("Chat with the AI")
    user_message = st.text_input("Type your message here:")
    if user_message:
        st.write("**AI Response:** This is where the chatbot's response would go!")

if __name__ == "__main__":
    main()
