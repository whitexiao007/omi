"""
Streamlit dashboard for MyTrans transcription application
"""

import streamlit as st
import requests
import json
import time
import websocket
import threading
import queue
import os
from typing import Optional
import tempfile

# Page configuration
st.set_page_config(
    page_title="MyTrans - Real-time Transcription",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .service-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .transcription-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        min-height: 200px;
        max-height: 400px;
        overflow-y: auto;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-connected { background-color: #28a745; }
    .status-disconnected { background-color: #dc3545; }
    .status-connecting { background-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcription_text' not in st.session_state:
    st.session_state.transcription_text = ""
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'websocket' not in st.session_state:
    st.session_state.websocket = None
if 'transcription_queue' not in st.session_state:
    st.session_state.transcription_queue = queue.Queue()

# API configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_services():
    """Get available transcription services from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/services", timeout=5)
        if response.status_code == 200:
            return response.json()["services"]
        return {}
    except:
        return {}

def transcribe_file(file, service):
    """Transcribe uploaded file"""
    try:
        files = {"file": file}
        data = {"service": service}
        response = requests.post(f"{API_BASE_URL}/transcribe/file", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

class WebSocketClient:
    """WebSocket client for real-time transcription"""
    
    def __init__(self, service, on_message_callback):
        self.service = service
        self.on_message_callback = on_message_callback
        self.ws = None
        self.is_connected = False
    
    def on_open(self, ws):
        self.is_connected = True
        st.session_state.is_streaming = True
        self.on_message_callback("🟢 Connected to transcription service")
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "transcription":
                self.on_message_callback(data.get("text", ""))
            elif data.get("type") == "status":
                self.on_message_callback(f"ℹ️ {data.get('message', '')}")
            elif data.get("type") == "error":
                self.on_message_callback(f"❌ Error: {data.get('message', '')}")
        except Exception as e:
            self.on_message_callback(f"❌ Error parsing message: {str(e)}")
    
    def on_error(self, ws, error):
        self.is_connected = False
        st.session_state.is_streaming = False
        self.on_message_callback(f"❌ WebSocket error: {str(error)}")
    
    def on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        st.session_state.is_streaming = False
        self.on_message_callback("🔴 Disconnected from transcription service")
    
    def connect(self):
        """Connect to WebSocket"""
        try:
            websocket_url = f"ws://localhost:8000/transcribe/stream/{self.service}"
            self.ws = websocket.WebSocketApp(
                websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            
        except Exception as e:
            self.on_message_callback(f"❌ Failed to connect: {str(e)}")
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
        st.session_state.is_streaming = False

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🎤 MyTrans</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Real-time Transcription with Multiple AI Services</p>', unsafe_allow_html=True)
    
    # Check API health
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ API server is not running. Please start the FastAPI server with: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Service selection
        services = get_available_services()
        if services:
            st.subheader("Available Services")
            for service_name, description in services.items():
                with st.expander(f"📡 {service_name.title()}"):
                    st.write(description)
        
        # API status
        st.subheader("API Status")
        if api_healthy:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
        
        # Environment check
        st.subheader("Environment")
        if os.getenv("OPENAI_API_KEY"):
            st.success("✅ OpenAI API Key Found")
        else:
            st.warning("⚠️ OpenAI API Key Not Found")
            st.info("Set OPENAI_API_KEY in your environment or .env file")
    
    # Main content
    tab1, tab2 = st.tabs(["📁 Record & Transcribe", "🎙️ Real-time Streaming"])
    
    with tab1:
        st.header("📁 Record & Transcribe")
        st.write("Upload an audio file and transcribe it using your chosen service.")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            help="Supported formats: WAV, MP3, M4A, FLAC, OGG"
        )
        
        # Service selection for file transcription
        service_options = list(services.keys()) if services else ["whisper", "gpt-4o-transcribe", "gpt-4o-realtime-preview"]
        selected_service = st.selectbox(
            "Select transcription service",
            service_options,
            help="Choose the AI service for transcription"
        )
        
        # Transcribe button
        if uploaded_file and st.button("🎯 Transcribe", type="primary"):
            with st.spinner("Transcribing audio..."):
                result = transcribe_file(uploaded_file, selected_service)
                
                if "error" in result:
                    st.error(f"Transcription failed: {result['error']}")
                else:
                    st.success("✅ Transcription completed!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 Transcription")
                        st.text_area(
                            "Transcribed text",
                            value=result.get("text", ""),
                            height=200,
                            disabled=True
                        )
                    
                    with col2:
                        st.subheader("📊 Details")
                        details = {
                            "Service": result.get("service", ""),
                            "Language": result.get("language", ""),
                            "Duration": f"{result.get('duration', 0):.2f}s" if result.get('duration') else "N/A",
                            "Segments": len(result.get("segments", []))
                        }
                        
                        for key, value in details.items():
                            st.metric(key, value)
                    
                    # Show segments if available
                    if result.get("segments"):
                        with st.expander("📋 View Segments"):
                            for i, segment in enumerate(result["segments"]):
                                st.write(f"**Segment {i+1}** ({segment.get('start', 0):.2f}s - {segment.get('end', 0):.2f}s)")
                                st.write(segment.get("text", ""))
                                st.divider()
    
    with tab2:
        st.header("🎙️ Real-time Streaming")
        st.write("Stream audio from your microphone in real-time.")
        
        # Service selection for streaming
        streaming_services = [s for s in service_options if s != "whisper"]  # Whisper doesn't support streaming
        selected_streaming_service = st.selectbox(
            "Select streaming service",
            streaming_services,
            help="Choose the AI service for real-time transcription (Whisper not available for streaming)"
        )
        
        # Streaming controls
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.is_streaming:
                if st.button("🎙️ Start Streaming", type="primary"):
                    # Initialize WebSocket client
                    def on_transcription_message(message):
                        st.session_state.transcription_text += message + "\n"
                        st.session_state.transcription_queue.put(message)
                    
                    st.session_state.websocket = WebSocketClient(selected_streaming_service, on_transcription_message)
                    st.session_state.websocket.connect()
                    st.rerun()
        
        with col2:
            if st.session_state.is_streaming:
                if st.button("⏹️ Stop Streaming"):
                    if st.session_state.websocket:
                        st.session_state.websocket.disconnect()
                    st.session_state.is_streaming = False
                    st.rerun()
        
        # Status indicator
        if st.session_state.is_streaming:
            st.success("🟢 Streaming active - Speak into your microphone")
        else:
            st.info("⏸️ Streaming stopped")
        
        # Real-time transcription display
        st.subheader("📝 Live Transcription")
        
        # Create a container for real-time updates
        transcription_container = st.container()
        
        with transcription_container:
            # Display current transcription
            st.text_area(
                "Live transcription",
                value=st.session_state.transcription_text,
                height=300,
                disabled=True,
                key="live_transcription"
            )
            
            # Clear button
            if st.button("🗑️ Clear Transcription"):
                st.session_state.transcription_text = ""
                st.rerun()
        
        # Handle real-time updates
        if st.session_state.is_streaming:
            # Check for new messages in the queue
            try:
                while not st.session_state.transcription_queue.empty():
                    message = st.session_state.transcription_queue.get_nowait()
                    # The message is already added to transcription_text in the callback
                    st.rerun()
            except queue.Empty:
                pass
            
            # Auto-refresh for real-time updates
            time.sleep(0.1)
            st.rerun()

if __name__ == "__main__":
    main()