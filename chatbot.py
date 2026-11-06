

import streamlit as st
from streamlit_chat import message
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import subprocess
import os
from pathlib import Path
from project_paths import WELLNESS_DATASET, CHAT_HISTORY_CSV, BASE_DIR
from auth import require_auth

if not require_auth():
    st.stop()


@st.cache_resource 
def cached_model():
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    return model


@st.cache_data  
def get_dataset():
    if not WELLNESS_DATASET.is_file():
        raise FileNotFoundError(f'Wellness dataset not found: {WELLNESS_DATASET}')
    df = pd.read_csv(WELLNESS_DATASET)
    required = {'User', 'Chatbot', 'embedding'}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f'Wellness dataset is missing required columns: {sorted(missing)}')
    def parse_embedding(value):
        if isinstance(value, list):
            return value
        parsed = json.loads(value) if isinstance(value, str) else value
        if not isinstance(parsed, list) or not parsed:
            raise ValueError('Dataset contains an empty or invalid embedding')
        return parsed
    df['embedding'] = df['embedding'].apply(parse_embedding)
    dimensions = {len(value) for value in df['embedding']}
    if len(dimensions) != 1:
        raise ValueError('Dataset embeddings have inconsistent dimensions')
    return df

try:
    model = cached_model()
    df = get_dataset()
except Exception as exc:
    st.error(f"The text chatbot could not load its model or dataset: {exc}")
    st.stop()


st.markdown("""
    <style>
        .header {
            background-color: #f1f1f1;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 2.5em;
            color: #333;
            border: 3px solid #d7bde2;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            font-weight: bold; /* Make the text bold */
            animation: fadeIn 2s ease-in-out; /* Animation for fading in */
        }

        /* Keyframes for fade-in animation */
        @keyframes fadeIn {
            0% {
                opacity: 0;
                transform: translateY(-20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Additional animation for sliding in */
        @keyframes slideIn {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(0);
            }
        }

    </style>
    <div class="header">
        Mindx 🤖
    </div>
""", unsafe_allow_html=True)



# Initialize session state if not already initialized
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Chat form to submit user input
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('You: ', '')
    
    submitted = st.form_submit_button('Send')

# Generate response from the chatbot
if submitted and user_input:
    embedding = model.encode(user_input)

    # Calculate cosine similarity and find the most similar response
    df['distance'] = df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())
    answer = df.loc[df['distance'].idxmax()]

    # Append user input and chatbot response to session state
    st.session_state.past.append(user_input)
    st.session_state.generated.append(answer['Chatbot'])

# Display chat history
for i in range(len(st.session_state['past'])):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    if len(st.session_state['generated']) > i:
        message(st.session_state['generated'][i], key=str(i) + '_bot')

def save_chat_history_to_csv():
    # Prepare the data
    chat_data = pd.DataFrame({
        'message': st.session_state['past'],
        'response': st.session_state['generated']
    })
    
    # Specify the path to the CSV file
    file_path = CHAT_HISTORY_CSV
    
    # If the file doesn't exist, create it and write headers, otherwise append new data
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if chat_data.empty:
        return
    if not file_path.exists():
        chat_data.to_csv(file_path, index=False, mode='w', header=True)
    else:
        chat_data.to_csv(file_path, index=False, mode='a', header=False)
    
# Function to truncate the CSV file (reset the chat history)
def truncate_csv():
    file_path = CHAT_HISTORY_CSV
    if os.path.exists(file_path):
        os.remove(file_path)
  

    
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
with st.sidebar:
    st.markdown("""
    <h1 style='color: black; font-size: 40px; font-weight: bold; text-align: center; 
              background-color: #f0f0f0; padding: 20px; border-radius: 10px;'>
        Welcome
    </h1>
""", unsafe_allow_html=True)

    # Display image in the sidebar with a specific width
    sidebar_image = BASE_DIR / '200w.gif'
    if sidebar_image.exists():
        st.image(str(sidebar_image), width=250)
    else:
        st.caption('Mindx wellness assistant')

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button('Save History'):
            save_chat_history_to_csv()
            st.success("Chat history saved!")

    with col2:
        if st.button('Clear History'):
            st.session_state['generated'] = []
            st.session_state['past'] = []
            st.session_state['past'] = []
            st.session_state['generated'] = []
            st.success("History cleared!")

    with col3:
        if st.button('Go to Login Page'):
            truncate_csv()
            st.info('Open the frontend login page in your browser. Authentication is not implemented by this prototype.')

    with col4:
        if st.button('Go to Routine'):
            save_chat_history_to_csv()
            import random

# Generate a random port to avoid clashes and open a new page each time
            port = random.randint(8500, 8600)  # choose a port within a range
            subprocess.Popen(["streamlit", "run", "sentimet.py", "--server.port", str(port)])
            st.success("Navigating to Yoga Routine...")