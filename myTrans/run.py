#!/usr/bin/env python3
"""
MyTrans Startup Script
Runs both the FastAPI backend and Streamlit dashboard
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import streamlit
        import openai
        import websocket
        import pyaudio
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy .env.example to .env and add your OpenAI API key")
        return False
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🎨 Starting Streamlit dashboard...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def main():
    """Main startup function"""
    print("🎤 MyTrans - Real-time Transcription Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        print("Continuing without .env file...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)
    
    # Wait a moment for API to start
    print("⏳ Waiting for API server to start...")
    time.sleep(3)
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        print("❌ Failed to start dashboard, stopping API server...")
        api_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ MyTrans is running!")
    print("📡 API Server: http://localhost:8000")
    print("🎨 Dashboard: http://localhost:8501")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 50)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            
            if dashboard_process.poll() is not None:
                print("❌ Dashboard stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping MyTrans...")
    
    finally:
        # Clean up processes
        if api_process:
            print("🛑 Stopping API server...")
            api_process.terminate()
            api_process.wait()
        
        if dashboard_process:
            print("🛑 Stopping dashboard...")
            dashboard_process.terminate()
            dashboard_process.wait()
        
        print("✅ MyTrans stopped")

if __name__ == "__main__":
    main()