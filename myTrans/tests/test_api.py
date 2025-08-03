"""
Tests for FastAPI endpoints
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "MyTrans API"
        assert data["version"] == "1.0.0"
        assert "services" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "MyTrans API is running"
    
    def test_services_endpoint(self):
        """Test services endpoint"""
        response = client.get("/services")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "whisper" in data["services"]
        assert "gpt-4o-transcribe" in data["services"]
        assert "gpt-4o-realtime-preview" in data["services"]
    
    @patch('main.transcription_manager')
    def test_transcribe_file_success(self, mock_manager):
        """Test successful file transcription"""
        # Mock the transcription manager
        mock_manager.transcribe_file.return_value = {
            "text": "Test transcription",
            "language": "en",
            "duration": 5.0,
            "service": "whisper"
        }
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/transcribe/file",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={"service": "whisper"}
                )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["text"] == "Test transcription"
            assert data["language"] == "en"
            assert data["service"] == "whisper"
            
        finally:
            os.unlink(temp_file_path)
    
    def test_transcribe_file_invalid_service(self):
        """Test file transcription with invalid service"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/transcribe/file",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={"service": "invalid_service"}
                )
            
            assert response.status_code == 400
            assert "Invalid service" in response.json()["detail"]
            
        finally:
            os.unlink(temp_file_path)
    
    def test_transcribe_file_invalid_file_type(self):
        """Test file transcription with invalid file type"""
        # Create temporary test file with invalid extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"fake data")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/transcribe/file",
                    files={"file": ("test.txt", f, "text/plain")},
                    data={"service": "whisper"}
                )
            
            assert response.status_code == 400
            assert "Invalid file type" in response.json()["detail"]
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('main.transcription_manager')
    def test_transcribe_file_api_error(self, mock_manager):
        """Test file transcription with API error"""
        # Mock the transcription manager to return error
        mock_manager.transcribe_file.return_value = {
            "error": "API Error occurred"
        }
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/transcribe/file",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={"service": "whisper"}
                )
            
            assert response.status_code == 500
            assert "API Error occurred" in response.json()["detail"]
            
        finally:
            os.unlink(temp_file_path)
    
    def test_start_streaming_invalid_service(self):
        """Test start streaming with invalid service"""
        response = client.post("/transcribe/stream/start", params={"service": "invalid_service"})
        
        assert response.status_code == 400
        assert "Invalid service" in response.json()["detail"]
    
    def test_start_streaming_whisper(self):
        """Test start streaming with Whisper (should fail)"""
        response = client.post("/transcribe/stream/start", params={"service": "whisper"})
        
        assert response.status_code == 400
        assert "Whisper doesn't support real-time streaming" in response.json()["detail"]
    
    def test_start_streaming_valid_service(self):
        """Test start streaming with valid service"""
        response = client.post("/transcribe/stream/start", params={"service": "gpt-4o-transcribe"})
        
        assert response.status_code == 200
        data = response.json()
        assert "Streaming started" in data["message"]
        assert "gpt-4o-transcribe" in data["message"]

class TestWebSocketEndpoints:
    """Test cases for WebSocket endpoints"""
    
    def test_websocket_invalid_service(self):
        """Test WebSocket connection with invalid service"""
        with client.websocket_connect("/transcribe/stream/invalid_service") as websocket:
            data = websocket.receive_json()
            assert "error" in data
            assert "Invalid service" in data["error"]
    
    def test_websocket_whisper_service(self):
        """Test WebSocket connection with Whisper (should fail)"""
        with client.websocket_connect("/transcribe/stream/whisper") as websocket:
            data = websocket.receive_json()
            assert "error" in data
            assert "Whisper doesn't support real-time streaming" in data["error"]
    
    @patch('main.transcription_manager')
    def test_websocket_valid_service(self, mock_manager):
        """Test WebSocket connection with valid service"""
        # Mock the transcription manager
        mock_manager.start_streaming.return_value = None
        
        with client.websocket_connect("/transcribe/stream/gpt-4o-transcribe") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert "Starting gpt-4o-transcribe transcription" in data["message"]

# Test utility functions
def test_cors_headers():
    """Test CORS headers are present"""
    response = client.get("/")
    assert "access-control-allow-origin" in response.headers

def test_api_documentation():
    """Test API documentation endpoints"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])