"""Shared, platform-independent paths for Mindx runtime data."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_DIR = DATA_DIR / "csv"
ANALYSIS_DIR = DATA_DIR / "analysis"
AUDIO_DIR = DATA_DIR / "audio"
RECORDING_DIR = AUDIO_DIR / "recordingAi"
VOICE_AUDIO_DIR = AUDIO_DIR / "Psychologist-Voice-Chatbot"
CONVERSATION_DIR = AUDIO_DIR / "conversation"
TRANSCRIPTIONS_CSV = CSV_DIR / "transcriptions.csv"
CHAT_HISTORY_CSV = ANALYSIS_DIR / "chat_history.csv"
WELLNESS_DATASET = BASE_DIR / "wellness_dataset.csv"

for directory in (DATA_DIR, CSV_DIR, ANALYSIS_DIR, AUDIO_DIR, RECORDING_DIR, VOICE_AUDIO_DIR, CONVERSATION_DIR):
    directory.mkdir(parents=True, exist_ok=True)
