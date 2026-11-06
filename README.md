# Mindx – AI-Powered Mental Wellbeing Chatbot

Mindx is an AI-powered mental-wellbeing web application that supports text- and voice-based conversations. It combines conversational AI, speech recognition, and sentiment analysis to provide wellbeing-related resources and recommendations.

## Features

- **Text Chatbot:** Uses Sentence Transformers and cosine similarity to retrieve relevant responses from a wellbeing dataset.
- **Voice Chatbot:** Supports voice recording, speech-to-text using Whisper, AI-generated responses through Groq, and text-to-speech.
- **Sentiment Analysis:** Uses TextBlob to analyse message sentiment and classify general mood.
- **Yoga Recommendations:** Provides yoga suggestions based on predicted mood.
- **Wellbeing Resources:** Offers relevant videos, music, and other wellbeing resources.
- **PDF Reports:** Generates downloadable reports containing sentiment-analysis results.
- **User Authentication:** Uses Flask and SQLite for registration and login.

## Technology Stack

- Python
- Flask
- Streamlit
- SQLite
- Sentence Transformers
- Scikit-learn
- Groq API
- Whisper
- LangChain
- TextBlob
- Pandas
- ReportLab
- HTML and CSS

## Project Structure

```text
Mindx/
├── templates/
│   ├── home.html
│   ├── login.html
│   └── register.html
├── auth_web.py
├── auth.py
├── chatbot.py
├── app.py
├── bot.py
├── sentimet.py
├── utils.py
├── yoga.py
├── project_paths.py
├── wellness_dataset.csv
├── requirements.txt
└── README.md
```

## Installation and Setup

1. Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

2. Create a virtual environment:

```bash
py -3.10 -m venv .venv
```

3. Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Configure your Groq API key as an environment variable if required:

```powershell
$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

6. Start the application:

```bash
python auth_web.py
```

7. Open the application:

```text
http://127.0.0.1:5500
```

## Notes

- Python 3.10 is used for the development environment.
- The voice interface requires the relevant API configuration and audio dependencies.
- Sentiment classifications indicate general text sentiment and are not clinical mental-health assessments.
- Do not upload API keys, passwords, private user records, databases, or session secrets to GitHub.

## Project Status

The application is under development. Authentication, chatbot integration, privacy controls, and user interface improvements are being reviewed and refined.

## Author

Preona Dsouza