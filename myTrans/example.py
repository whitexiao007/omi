"""
Example script demonstrating MyTrans transcription functionality
"""

import asyncio
import os
import tempfile
from transcribe import TranscriptionManager

async def example_file_transcription():
    """Example of file transcription"""
    print("=== File Transcription Example ===")
    
    # Initialize transcription manager
    manager = TranscriptionManager()
    
    # Create a simple test audio file (this would normally be a real audio file)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        # Write some dummy audio data (in practice, this would be real audio)
        temp_file.write(b"fake audio data for testing")
        temp_file_path = temp_file.name
    
    try:
        # Test with Whisper
        print("\n1. Testing Whisper transcription...")
        result = await manager.transcribe_file(temp_file_path, "whisper")
        if "error" in result:
            print(f"Whisper error: {result['error']}")
        else:
            print(f"Whisper result: {result['text']}")
        
        # Test with GPT-4o-transcribe
        print("\n2. Testing GPT-4o-transcribe...")
        result = await manager.transcribe_file(temp_file_path, "gpt-4o-transcribe")
        if "error" in result:
            print(f"GPT-4o-transcribe error: {result['error']}")
        else:
            print(f"GPT-4o-transcribe result: {result['text']}")
        
        # Test with GPT-4o-realtime-preview
        print("\n3. Testing GPT-4o-realtime-preview...")
        result = await manager.transcribe_file(temp_file_path, "gpt-4o-realtime-preview")
        if "error" in result:
            print(f"GPT-4o-realtime-preview error: {result['error']}")
        else:
            print(f"GPT-4o-realtime-preview result: {result['text']}")
    
    finally:
        # Clean up
        os.unlink(temp_file_path)

def example_streaming():
    """Example of real-time streaming (commented out as it requires microphone)"""
    print("\n=== Real-time Streaming Example ===")
    print("Note: This example is commented out as it requires microphone access.")
    print("To test real-time streaming, use the Streamlit dashboard or WebSocket API.")
    
    # Example code (commented out):
    """
    async def streaming_callback(text):
        print(f"Received: {text}")
    
    manager = TranscriptionManager()
    
    # Start streaming with GPT-4o-transcribe
    print("Starting real-time streaming with GPT-4o-transcribe...")
    print("Speak into your microphone (press Ctrl+C to stop)")
    
    try:
        await manager.start_streaming("gpt-4o-transcribe", streaming_callback)
    except KeyboardInterrupt:
        print("\nStopping streaming...")
    """

def example_available_services():
    """Example of getting available services"""
    print("=== Available Services ===")
    
    manager = TranscriptionManager()
    services = manager.get_available_services()
    
    for service_name, description in services.items():
        print(f"\n{service_name.upper()}:")
        print(f"  {description}")

async def main():
    """Main example function"""
    print("🎤 MyTrans Transcription Examples")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Set it in your .env file or environment variables")
        print("   Some examples may not work without the API key")
        print()
    
    # Show available services
    example_available_services()
    
    # File transcription example
    await example_file_transcription()
    
    # Streaming example (commented out)
    example_streaming()
    
    print("\n" + "=" * 50)
    print("✅ Examples completed!")
    print("\nTo run the full application:")
    print("1. Start the API: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Start the dashboard: streamlit run dashboard.py")
    print("3. Open http://localhost:8501 in your browser")

if __name__ == "__main__":
    asyncio.run(main())