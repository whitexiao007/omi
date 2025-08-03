"""
FastAPI backend for MyTrans transcription application
"""

import os
import tempfile
import shutil
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from transcribe import TranscriptionManager
import asyncio
import json

app = FastAPI(
    title="MyTrans API",
    description="Real-time transcription API supporting Whisper, GPT-4o-transcribe, and GPT-4o-realtime-preview",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize transcription manager
transcription_manager = TranscriptionManager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MyTrans API",
        "version": "1.0.0",
        "services": transcription_manager.get_available_services()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "MyTrans API is running"}

@app.get("/services")
async def get_services():
    """Get available transcription services"""
    return {
        "services": transcription_manager.get_available_services()
    }

@app.post("/transcribe/file")
async def transcribe_file(
    file: UploadFile = File(...),
    service: str = "whisper"
):
    """
    Transcribe uploaded audio file
    
    Args:
        file: Audio file to transcribe
        service: Transcription service to use (whisper, gpt-4o-transcribe, gpt-4o-realtime-preview)
    
    Returns:
        Transcription result with text, language, duration, and segments
    """
    # Validate service
    available_services = transcription_manager.get_available_services()
    if service not in available_services:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service. Available services: {list(available_services.keys())}"
        )
    
    # Validate file type
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {allowed_extensions}"
        )
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Transcribe the file
        result = await transcription_manager.transcribe_file(temp_file_path, service)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.websocket("/transcribe/stream/{service}")
async def transcribe_stream(websocket: WebSocket, service: str):
    """
    WebSocket endpoint for real-time streaming transcription
    
    Args:
        websocket: WebSocket connection
        service: Transcription service to use
    """
    await websocket.accept()
    
    # Validate service
    available_services = transcription_manager.get_available_services()
    if service not in available_services:
        await websocket.send_text(json.dumps({
            "error": f"Invalid service. Available services: {list(available_services.keys())}"
        }))
        await websocket.close()
        return
    
    # Check if service supports streaming
    if service == "whisper":
        await websocket.send_text(json.dumps({
            "error": "Whisper doesn't support real-time streaming. Use gpt-4o-transcribe or gpt-4o-realtime-preview."
        }))
        await websocket.close()
        return
    
    def callback(text: str):
        """Callback function to send transcription results to WebSocket"""
        try:
            asyncio.create_task(websocket.send_text(json.dumps({
                "type": "transcription",
                "text": text
            })))
        except Exception as e:
            print(f"Error sending to WebSocket: {e}")
    
    try:
        # Start streaming transcription
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": f"Starting {service} transcription..."
        }))
        
        # Run streaming in a separate task
        streaming_task = asyncio.create_task(
            transcription_manager.start_streaming(service, callback)
        )
        
        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "stop":
                    # Client requested to stop streaming
                    break
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                }))
    
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Streaming error: {str(e)}"
        }))
    
    finally:
        # Clean up
        if 'streaming_task' in locals():
            streaming_task.cancel()
        
        await websocket.close()

@app.post("/transcribe/stream/start")
async def start_streaming(service: str):
    """
    Start real-time streaming transcription (alternative to WebSocket)
    
    Args:
        service: Transcription service to use
    
    Returns:
        Status message
    """
    # Validate service
    available_services = transcription_manager.get_available_services()
    if service not in available_services:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service. Available services: {list(available_services.keys())}"
        )
    
    if service == "whisper":
        raise HTTPException(
            status_code=400,
            detail="Whisper doesn't support real-time streaming. Use gpt-4o-transcribe or gpt-4o-realtime-preview."
        )
    
    return {
        "message": f"Streaming started with {service}",
        "note": "Use WebSocket endpoint /transcribe/stream/{service} for real-time communication"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )