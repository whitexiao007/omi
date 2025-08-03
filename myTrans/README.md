# MyTrans - Real-time Transcription Application

A simple transcription application that supports multiple transcription services including Whisper, GPT-4o-transcribe, and GPT-4o-realtime-preview.

## Features

- **Record and Transcribe**: Upload audio files and transcribe them using different services
- **Real-time Streaming**: Stream audio from microphone in real-time
- **Multiple Transcription Services**:
  - OpenAI Whisper (file-based transcription)
  - GPT-4o-transcribe (real-time transcription)
  - GPT-4o-realtime-preview (real-time with AI capabilities)

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
Create a `.env` file in the myTrans directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Run the application**:
```bash
# Run the FastAPI backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run the Streamlit dashboard (in another terminal)
streamlit run dashboard.py
```

## Usage

### Web Dashboard
- Open http://localhost:8501 in your browser
- Choose between "Record & Transcribe" or "Real-time Streaming"
- Select your preferred transcription service
- Start recording or streaming

### API Endpoints
- `POST /transcribe/file` - Transcribe uploaded audio file
- `POST /transcribe/stream` - Start real-time streaming transcription
- `GET /health` - Health check endpoint

## Testing

Run the tests with:
```bash
pytest tests/
```

## Project Structure

```
myTrans/
├── main.py              # FastAPI backend
├── dashboard.py         # Streamlit dashboard
├── transcribe.py        # Transcription services
├── tests/              # Test files
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Supported Audio Formats

- WAV, MP3, M4A, FLAC (for file uploads)
- Real-time PCM audio (for streaming)

## Notes

- Real-time streaming requires microphone access
- GPT-4o services require OpenAI API key
- Whisper works offline for file transcription