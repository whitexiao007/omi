"""
Tests for transcription services
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from transcribe import (
    TranscriptionManager,
    WhisperService,
    GPT4oTranscribeService,
    GPT4oRealtimePreviewService
)

class TestTranscriptionManager:
    """Test cases for TranscriptionManager"""
    
    def setup_method(self):
        """Setup method for each test"""
        self.manager = TranscriptionManager()
    
    def test_get_available_services(self):
        """Test getting available services"""
        services = self.manager.get_available_services()
        
        assert "whisper" in services
        assert "gpt-4o-transcribe" in services
        assert "gpt-4o-realtime-preview" in services
        
        assert "OpenAI Whisper" in services["whisper"]
        assert "GPT-4o Transcribe" in services["gpt-4o-transcribe"]
        assert "GPT-4o Realtime Preview" in services["gpt-4o-realtime-preview"]
    
    def test_get_service(self):
        """Test getting service by name"""
        whisper_service = self.manager.get_service("whisper")
        gpt4o_service = self.manager.get_service("gpt-4o-transcribe")
        realtime_service = self.manager.get_service("gpt-4o-realtime-preview")
        
        assert isinstance(whisper_service, WhisperService)
        assert isinstance(gpt4o_service, GPT4oTranscribeService)
        assert isinstance(realtime_service, GPT4oRealtimePreviewService)
        
        # Test invalid service
        invalid_service = self.manager.get_service("invalid")
        assert invalid_service is None

class TestWhisperService:
    """Test cases for WhisperService"""
    
    def setup_method(self):
        """Setup method for each test"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            self.service = WhisperService()
    
    @patch('transcribe.OpenAI')
    async def test_transcribe_file_success(self, mock_openai):
        """Test successful file transcription"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Hello, this is a test transcription."
        mock_response.language = "en"
        mock_response.duration = 5.0
        mock_response.segments = [{"start": 0, "end": 5, "text": "Hello, this is a test transcription."}]
        
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            result = await self.service.transcribe_file(temp_file_path)
            
            assert result["text"] == "Hello, this is a test transcription."
            assert result["language"] == "en"
            assert result["duration"] == 5.0
            assert result["service"] == "whisper"
            assert len(result["segments"]) == 1
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('transcribe.OpenAI')
    async def test_transcribe_file_error(self, mock_openai):
        """Test file transcription with error"""
        # Mock OpenAI client to raise exception
        mock_client = Mock()
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            result = await self.service.transcribe_file(temp_file_path)
            
            assert "error" in result
            assert "API Error" in result["error"]
            assert result["service"] == "whisper"
            
        finally:
            os.unlink(temp_file_path)
    
    async def test_start_streaming_not_implemented(self):
        """Test that Whisper doesn't support streaming"""
        with pytest.raises(NotImplementedError, match="Whisper doesn't support real-time streaming"):
            await self.service.start_streaming(lambda x: None)

class TestGPT4oTranscribeService:
    """Test cases for GPT4oTranscribeService"""
    
    def setup_method(self):
        """Setup method for each test"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            self.service = GPT4oTranscribeService()
    
    @patch('transcribe.OpenAI')
    async def test_transcribe_file_success(self, mock_openai):
        """Test successful file transcription"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "GPT-4o transcription test."
        mock_response.language = "en"
        mock_response.duration = 3.5
        mock_response.segments = [{"start": 0, "end": 3.5, "text": "GPT-4o transcription test."}]
        
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            result = await self.service.transcribe_file(temp_file_path)
            
            assert result["text"] == "GPT-4o transcription test."
            assert result["language"] == "en"
            assert result["duration"] == 3.5
            assert result["service"] == "gpt-4o-transcribe"
            
        finally:
            os.unlink(temp_file_path)

class TestGPT4oRealtimePreviewService:
    """Test cases for GPT4oRealtimePreviewService"""
    
    def setup_method(self):
        """Setup method for each test"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            self.service = GPT4oRealtimePreviewService()
    
    @patch('transcribe.OpenAI')
    async def test_transcribe_file_success(self, mock_openai):
        """Test successful file transcription"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "GPT-4o realtime preview test."
        mock_response.language = "en"
        mock_response.duration = 4.2
        mock_response.segments = [{"start": 0, "end": 4.2, "text": "GPT-4o realtime preview test."}]
        
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_file_path = temp_file.name
        
        try:
            result = await self.service.transcribe_file(temp_file_path)
            
            assert result["text"] == "GPT-4o realtime preview test."
            assert result["language"] == "en"
            assert result["duration"] == 4.2
            assert result["service"] == "gpt-4o-realtime-preview"
            
        finally:
            os.unlink(temp_file_path)

# Integration tests
class TestIntegration:
    """Integration tests for the transcription system"""
    
    def setup_method(self):
        """Setup method for each test"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            self.manager = TranscriptionManager()
    
    async def test_manager_transcribe_file(self):
        """Test manager's transcribe_file method"""
        with patch('transcribe.OpenAI') as mock_openai:
            # Mock OpenAI client
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Integration test transcription."
            mock_response.language = "en"
            mock_response.duration = 2.0
            mock_response.segments = []
            
            mock_client.audio.transcriptions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # Create temporary test file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(b"fake audio data")
                temp_file_path = temp_file.name
            
            try:
                result = await self.manager.transcribe_file(temp_file_path, "whisper")
                
                assert result["text"] == "Integration test transcription."
                assert result["service"] == "whisper"
                
            finally:
                os.unlink(temp_file_path)
    
    def test_manager_invalid_service(self):
        """Test manager with invalid service"""
        result = asyncio.run(self.manager.transcribe_file("test.wav", "invalid_service"))
        
        assert "error" in result
        assert "not found" in result["error"]
    
    async def test_manager_streaming_invalid_service(self):
        """Test manager streaming with invalid service"""
        with pytest.raises(ValueError, match="Service invalid_service not found"):
            await self.manager.start_streaming("invalid_service", lambda x: None)

# Utility function for running tests
def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests()