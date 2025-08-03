# MyTrans Project Summary

## 🎯 Project Overview

MyTrans is a comprehensive real-time transcription application that supports multiple AI-powered transcription services. Built with FastAPI backend and Streamlit dashboard, it provides both file-based transcription and real-time streaming capabilities.

## 🏗️ Architecture

### Backend (FastAPI)
- **main.py**: FastAPI application with REST and WebSocket endpoints
- **transcribe.py**: Core transcription services module
- **API Endpoints**:
  - `GET /` - Root endpoint with service information
  - `GET /health` - Health check
  - `GET /services` - Available transcription services
  - `POST /transcribe/file` - File transcription
  - `POST /transcribe/stream/start` - Start streaming
  - `WebSocket /transcribe/stream/{service}` - Real-time streaming

### Frontend (Streamlit)
- **dashboard.py**: Interactive web dashboard
- **Features**:
  - File upload and transcription
  - Real-time streaming from microphone
  - Service selection and configuration
  - Live transcription display
  - Status monitoring

### Transcription Services
1. **Whisper** (`whisper`): OpenAI's Whisper model for file transcription
2. **GPT-4o-transcribe** (`gpt-4o-transcribe`): Real-time transcription service
3. **GPT-4o-realtime-preview** (`gpt-4o-realtime-preview`): Real-time transcription with AI capabilities

## 📁 Project Structure

```
myTrans/
├── main.py                 # FastAPI backend application
├── dashboard.py            # Streamlit dashboard
├── transcribe.py           # Core transcription services
├── run.py                  # Startup script
├── example.py              # Example usage script
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .env.example           # Environment configuration template
├── PROJECT_SUMMARY.md     # This file
└── tests/                 # Test suite
    ├── __init__.py
    ├── test_transcribe.py # Transcription service tests
    └── test_api.py        # API endpoint tests
```

## 🚀 Getting Started

### 1. Installation
```bash
cd myTrans
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Running the Application

#### Option A: Using the startup script
```bash
python run.py
```

#### Option B: Manual startup
```bash
# Terminal 1: Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start dashboard
streamlit run dashboard.py
```

### 4. Access the Application
- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_transcribe.py
pytest tests/test_api.py

# Run with verbose output
pytest tests/ -v
```

## 🔧 Key Features

### File Transcription
- Support for multiple audio formats (WAV, MP3, M4A, FLAC, OGG)
- Three transcription service options
- Detailed results with language detection and timing
- Segment-level transcription data

### Real-time Streaming
- Live microphone input
- WebSocket-based communication
- Real-time transcription display
- Support for GPT-4o services (Whisper not available for streaming)

### Dashboard Features
- Modern, responsive UI
- Real-time status monitoring
- Service selection and configuration
- File upload with drag-and-drop
- Live transcription display with auto-scroll

## 🔌 API Usage

### File Transcription
```bash
curl -X POST "http://localhost:8000/transcribe/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "service=whisper"
```

### Real-time Streaming (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8000/transcribe/stream/gpt-4o-transcribe');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.text);
};
```

## 🛠️ Development

### Adding New Transcription Services
1. Create a new service class inheriting from `TranscriptionService`
2. Implement `transcribe_file()` and optionally `start_streaming()`
3. Add the service to `TranscriptionManager`
4. Update tests and documentation

### Extending the Dashboard
- Modify `dashboard.py` for UI changes
- Add new Streamlit components as needed
- Update API calls for new features

### Testing
- Add new test cases in `tests/`
- Use mocking for external API calls
- Test both success and error scenarios

## 🔒 Security Considerations

- API key management via environment variables
- Input validation for file uploads
- CORS configuration for web access
- Error handling and logging

## 📊 Performance

- Asynchronous processing for file transcription
- WebSocket streaming for real-time audio
- Efficient audio processing with PyAudio
- Memory management for temporary files

## 🐛 Troubleshooting

### Common Issues
1. **Microphone not working**: Check system audio permissions
2. **API key errors**: Verify OPENAI_API_KEY in .env file
3. **Port conflicts**: Change ports in run.py or use different ports
4. **Dependency issues**: Reinstall with `pip install -r requirements.txt`

### Debug Mode
```bash
# Run with debug logging
uvicorn main:app --reload --log-level debug
```

## 📈 Future Enhancements

- Support for more audio formats
- Additional transcription services
- User authentication and management
- Conversation history and storage
- Multi-language support
- Audio preprocessing options
- Export functionality (PDF, SRT, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of the Omi ecosystem and follows the same licensing terms.

---

**MyTrans** - Real-time transcription with multiple AI services