"""
Transcription services module supporting Whisper, GPT-4o-transcribe, and GPT-4o-realtime-preview
"""

import os
import json
import base64
import time
import threading
import asyncio
from typing import Optional, Dict, Any, Callable
import websocket
import pyaudio
import soundfile as sf
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    """Base class for transcription services"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file"""
        raise NotImplementedError
    
    async def start_streaming(self, callback: Callable[[str], None]) -> None:
        """Start real-time streaming transcription"""
        raise NotImplementedError

class WhisperService(TranscriptionService):
    """Whisper transcription service for file-based transcription"""
    
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": transcript.segments if hasattr(transcript, 'segments') else [],
                "service": "whisper"
            }
        except Exception as e:
            return {
                "error": str(e),
                "service": "whisper"
            }
    
    async def start_streaming(self, callback: Callable[[str], None]) -> None:
        """Whisper doesn't support real-time streaming"""
        raise NotImplementedError("Whisper doesn't support real-time streaming")

class GPT4oTranscribeService(TranscriptionService):
    """GPT-4o-transcribe service for real-time transcription"""
    
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file using GPT-4o-transcribe"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": transcript.segments if hasattr(transcript, 'segments') else [],
                "service": "gpt-4o-transcribe"
            }
        except Exception as e:
            return {
                "error": str(e),
                "service": "gpt-4o-transcribe"
            }
    
    async def start_streaming(self, callback: Callable[[str], None]) -> None:
        """Start real-time streaming with GPT-4o-transcribe"""
        api_key = os.getenv("OPENAI_API_KEY")
        uri = "wss://api.openai.com/v1/realtime?api-version=2025-04-01-preview&deployment=gpt-4o-transcribe&intent=transcription"
        
        def on_open(ws):
            ws.send(json.dumps({
                "type": "session.update",
                "session": {
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "input_audio_transcription": {
                        "model": "gpt-4o-transcribe",
                        "language": "en"
                    }
                }
            }))
            
            def stream_audio():
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    input=True,
                    frames_per_buffer=2400
                )
                
                while ws.keep_running:
                    try:
                        data = stream.read(2400, exception_on_overflow=False)
                        b64 = base64.b64encode(data).decode()
                        ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": b64
                        }))
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Audio streaming error: {e}")
                        break
                
                stream.stop_stream()
                stream.close()
                audio.terminate()
            
            threading.Thread(target=stream_audio, daemon=True).start()
        
        def on_message(ws, msg):
            try:
                m = json.loads(msg)
                t = m.get("type", "")
                
                if t == "conversation.item.input_audio_transcription.delta":
                    delta = m.get("delta", "")
                    if delta:
                        callback(delta)
                
                elif t == "conversation.item.input_audio_transcription.completed":
                    final_text = m.get("transcript", "")
                    if final_text:
                        callback(f"\n[FINAL] {final_text}\n")
                
                elif t == "error":
                    error_msg = m.get("error", {}).get("message", "Unknown error")
                    callback(f"\n[ERROR] {error_msg}\n")
                    
            except Exception as e:
                callback(f"\n[ERROR] Message parsing error: {e}\n")
        
        def on_error(ws, error):
            callback(f"\n[ERROR] WebSocket error: {error}\n")
        
        def on_close(ws, close_status_code, close_msg):
            callback("\n[INFO] WebSocket connection closed\n")
        
        ws = websocket.WebSocketApp(
            uri,
            header={"Authorization": f"Bearer {api_key}"},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        ws.run_forever()

class GPT4oRealtimePreviewService(TranscriptionService):
    """GPT-4o-realtime-preview service for real-time transcription with AI capabilities"""
    
    async def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file using GPT-4o-realtime-preview"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="gpt-4o-realtime-preview",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": transcript.segments if hasattr(transcript, 'segments') else [],
                "service": "gpt-4o-realtime-preview"
            }
        except Exception as e:
            return {
                "error": str(e),
                "service": "gpt-4o-realtime-preview"
            }
    
    async def start_streaming(self, callback: Callable[[str], None]) -> None:
        """Start real-time streaming with GPT-4o-realtime-preview"""
        api_key = os.getenv("OPENAI_API_KEY")
        uri = "wss://api.openai.com/v1/realtime?api-version=2025-04-01-preview&deployment=gpt-4o-realtime-preview&intent=transcription"
        
        def on_open(ws):
            ws.send(json.dumps({
                "type": "session.update",
                "session": {
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "input_audio_transcription": {
                        "model": "gpt-4o-realtime-preview",
                        "language": "en"
                    }
                }
            }))
            
            def stream_audio():
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    input=True,
                    frames_per_buffer=2400
                )
                
                while ws.keep_running:
                    try:
                        data = stream.read(2400, exception_on_overflow=False)
                        b64 = base64.b64encode(data).decode()
                        ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": b64
                        }))
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Audio streaming error: {e}")
                        break
                
                stream.stop_stream()
                stream.close()
                audio.terminate()
            
            threading.Thread(target=stream_audio, daemon=True).start()
        
        def on_message(ws, msg):
            try:
                m = json.loads(msg)
                t = m.get("type", "")
                
                if t == "conversation.item.input_audio_transcription.delta":
                    delta = m.get("delta", "")
                    if delta:
                        callback(delta)
                
                elif t == "conversation.item.input_audio_transcription.completed":
                    final_text = m.get("transcript", "")
                    if final_text:
                        callback(f"\n[FINAL] {final_text}\n")
                
                elif t == "response.text.delta":
                    # AI response capability
                    delta = m.get("delta", "")
                    if delta:
                        callback(f"[AI] {delta}")
                
                elif t == "error":
                    error_msg = m.get("error", {}).get("message", "Unknown error")
                    callback(f"\n[ERROR] {error_msg}\n")
                    
            except Exception as e:
                callback(f"\n[ERROR] Message parsing error: {e}\n")
        
        def on_error(ws, error):
            callback(f"\n[ERROR] WebSocket error: {error}\n")
        
        def on_close(ws, close_status_code, close_msg):
            callback("\n[INFO] WebSocket connection closed\n")
        
        ws = websocket.WebSocketApp(
            uri,
            header={"Authorization": f"Bearer {api_key}"},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        ws.run_forever()

class TranscriptionManager:
    """Manager class for handling different transcription services"""
    
    def __init__(self):
        self.services = {
            "whisper": WhisperService(),
            "gpt-4o-transcribe": GPT4oTranscribeService(),
            "gpt-4o-realtime-preview": GPT4oRealtimePreviewService()
        }
    
    def get_service(self, service_name: str) -> Optional[TranscriptionService]:
        """Get transcription service by name"""
        return self.services.get(service_name)
    
    async def transcribe_file(self, audio_file_path: str, service_name: str) -> Dict[str, Any]:
        """Transcribe file using specified service"""
        service = self.get_service(service_name)
        if not service:
            return {"error": f"Service {service_name} not found"}
        
        return await service.transcribe_file(audio_file_path)
    
    async def start_streaming(self, service_name: str, callback: Callable[[str], None]) -> None:
        """Start streaming with specified service"""
        service = self.get_service(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found")
        
        await service.start_streaming(callback)
    
    def get_available_services(self) -> Dict[str, str]:
        """Get list of available services with descriptions"""
        return {
            "whisper": "OpenAI Whisper - File-based transcription (offline capable)",
            "gpt-4o-transcribe": "GPT-4o Transcribe - Real-time transcription service",
            "gpt-4o-realtime-preview": "GPT-4o Realtime Preview - Real-time transcription with AI capabilities"
        }