# Omi Codebase Analysis: Real-time Transcription Stack and App Development

## Overview
Omi is an AI-powered wearable device ecosystem consisting of hardware, firmware, mobile apps, and backend services that provide real-time conversation transcription and AI-powered apps/plugins. The platform now includes Model Context Protocol (MCP) integration, enhanced OAuth capabilities, and improved LLM processing with GPT-4.1.

## Architecture Stack

### 1. Device Architecture

#### Hardware
- Multiple hardware variants available:
  - Triangle v1 and v2 designs
  - Circle design
  - DevKit1 and DevKit2 for development
- Audio capture capabilities for real-time transcription
- Bluetooth connectivity for data streaming

#### Firmware
- **Platform**: Zephyr RTOS
- **Build System**: CMake with nRF Connect for VS Code or Docker
- **Location**: `/omi/firmware/`
- **Key Features**:
  - Audio capture and processing
  - Bluetooth Low Energy (BLE) connectivity
  - Battery management
  - Real-time audio streaming to mobile app

#### Device Connection Protocol
- **Technology**: Bluetooth Low Energy (BLE)
- **Service UUIDs**: 
  - Omi Service UUID for main functionality
  - Frame Service UUID for alternative devices
- **Audio Codec Support**: PCM8, other codecs available
- **Sample Rates**: Configurable (8000 Hz default)
- **Connection Management**: Handled by `DeviceService` in Flutter app

### 2. Mobile App Stack (Flutter)

#### Core Technologies
- **Framework**: Flutter (Dart)
- **State Management**: Provider pattern
- **Platform Support**: iOS, Android, macOS, Linux, Windows
- **Key Dependencies**:
  - `flutter_blue_plus`: BLE connectivity
  - `firebase_core`, `firebase_auth`: Authentication
  - `intercom_flutter`, `mixpanel_flutter`: Analytics
  - `provider`: State management

#### Real-time Audio Processing
- **Audio Capture**: From connected Omi device via BLE
- **Streaming**: Real-time audio bytes sent to backend via WebSocket
- **Transcription Service**: `TranscriptSegmentSocketService`
- **Connection Types**:
  - `ConversationTranscriptSegmentSocketService`: For conversations
  - `SpeechProfileTranscriptSegmentSocketService`: For speech profiling

#### Key Services
1. **Device Management** (`DeviceService`)
   - Device discovery and connection
   - BLE communication handling
   - Connection state management

2. **Audio Capture** (`CaptureProvider`)
   - Real-time audio streaming
   - Transcription service coordination
   - Memory/conversation creation

3. **WebSocket Communication** (`TranscriptSegmentSocketService`)
   - Real-time transcription streaming
   - Bidirectional communication with backend
   - Message event handling

### 3. Backend Stack (Python/FastAPI)

#### Core Technologies
- **Framework**: FastAPI
- **Deployment**: Modal for serverless functions
- **Database**: Firebase Firestore + Vector Database (Pinecone)
- **Real-time**: WebSocket connections
- **Authentication**: Firebase Auth + OAuth 2.0
- **LLM Models**: 
  - GPT-4.1 (llm_medium_experiment) for enhanced conversation processing
  - GPT-4o-mini for lightweight tasks
  - O1-preview for complex reasoning
  - Anthropic Claude 3.5 Sonnet (via OpenRouter)
  - Google Gemini Flash 1.5-8B (via OpenRouter)

#### Real-time Transcription Pipeline

1. **WebSocket Endpoint**: `/v4/listen`
   - Accepts audio streams from mobile apps
   - Parameters: language, sample_rate, codec, uid, speech_profile, stt_service
   - Supports multiple STT services (Soniox, Deepgram, Speechmatics)

2. **Transcription Services**:
   - **Soniox**: WebSocket-based real-time transcription
   - **Deepgram**: Enhanced with improved autoscaling policies, supports self-hosted deployments
   - **Speechmatics**: Another STT option
   - Multi-language support with automatic language detection
   - Configurable via user preferences

3. **Real-time Processing**:
   - Audio chunks processed in real-time
   - Transcript segments returned immediately
   - Speaker diarization support
   - Language detection and processing

### 4. App/Plugin Development Framework

#### Plugin Architecture
- **Location**: `/plugins/` directory
- **Framework**: FastAPI-based microservices
- **Types**:
  - Real-time plugins (process transcript segments immediately)
  - Memory-created plugins (process completed conversations)
  - External integrations (webhooks, actions)

#### Plugin Development Structure
```python
# Example real-time plugin
@router.post('/your-plugin', response_model=EndpointResponse)
def your_plugin(data: RealtimePluginRequest):
    # Process real-time transcript segments
    transcript = TranscriptSegment.segments_as_string(data.segments)
    # Your processing logic here
    return {'message': 'Your response'}
```

#### Plugin Categories
- Conversation Analysis
- Personality Emulation
- Health and Wellness
- Education and Learning
- Communication Improvement
- Emotional and Mental Support
- Productivity and Organization
- Entertainment and Fun
- Financial
- Travel and Exploration
- Safety and Security
- Shopping and Commerce
- Social and Relationships
- News and Information
- Utilities and Tools

#### App Management API
- **Endpoints**: `/v1/apps/*` in `backend/routers/apps.py`
- **Features**:
  - App creation, updating, deletion
  - App approval workflow
  - Review system
  - Payment integration for paid apps
  - External integrations (webhooks, actions)

### 5. Knowledge Base and Vector Storage

#### Vector Database Integration
- **Database**: Pinecone for vector storage
- **Embeddings**: OpenAI text-embedding-3-large model
- **Purpose**: Store conversation memories as searchable vectors
- **Implementation**: `/backend/database/vector_db.py`

#### Knowledge Base Features
- **Memory Storage**: Conversations converted to structured format and vectorized
- **Retrieval**: RAG (Retrieval Augmented Generation) for context-aware responses
- **Search**: Vector similarity search for relevant memories
- **Metadata Filtering**: Time-based and topic-based filtering

#### Conversation Processing Pipeline
1. **Real-time Transcription**: Live audio → transcript segments
2. **Conversation Creation**: Segments assembled into conversations
3. **Structured Extraction**: AI extracts structured data (title, summary, topics) using GPT-4.1
4. **Vector Generation**: Embeddings created for semantic search
5. **Storage**: Vectors stored with metadata for retrieval
6. **MCP Integration**: Conversations and memories accessible via Model Context Protocol

## Developing Real-time Advice Apps

### Steps to Create Real-time Conversation Apps

#### 1. Set Up Development Environment
```bash
# Clone the repository
git clone https://github.com/BasedHardware/Omi.git
cd Omi

# Set up plugin development
cd plugins/example
pip install -r requirements.txt
```

#### 2. Create Real-time Plugin
```python
# plugins/your-app/realtime.py
from fastapi import APIRouter
from models import RealtimePluginRequest, EndpointResponse

router = APIRouter()

@router.post('/real-time-advice', response_model=EndpointResponse)
def real_time_advice(data: RealtimePluginRequest):
    # Access current transcript segments
    transcript = TranscriptSegment.segments_as_string(data.segments)
    
    # Your advice logic here
    advice = generate_advice(transcript)
    
    if advice:
        return {'message': advice}
    return {}
```

#### 3. Add Knowledge Base Integration
```python
# Use vector search for contextual advice
def generate_contextual_advice(transcript: str, uid: str):
    # Query vector database for relevant memories
    from database.vector_db import query_vectors
    
    relevant_memories = query_vectors(
        query=transcript,
        uid=uid,
        k=5  # Top 5 relevant memories
    )
    
    # Use memories for context-aware advice
    context = prepare_context(relevant_memories)
    advice = llm_generate_advice(transcript, context)
    
    return advice
```

#### 4. Add Web Search Integration
```python
# Integrate web search for current information
import requests

def get_web_context(query: str):
    # Use search API (Tavily, Serper, etc.)
    search_results = search_api.search(query)
    return extract_relevant_info(search_results)

@router.post('/advice-with-web-search', response_model=EndpointResponse)
def advice_with_web_search(data: RealtimePluginRequest):
    transcript = TranscriptSegment.segments_as_string(data.segments)
    
    # Extract key topics for web search
    topics = extract_topics(transcript)
    
    # Get current web information
    web_context = get_web_context(topics)
    
    # Generate advice with web context
    advice = generate_advice_with_context(transcript, web_context)
    
    return {'message': advice} if advice else {}
```

#### 5. Integrate MCP for Enhanced Context
```python
# Use MCP to access conversation history and memories
import requests

async def get_mcp_context(uid: str, current_topic: str):
    # Access memories via MCP API
    memories_response = requests.get(
        f"https://api-url/v1/mcp/memories?uid={uid}&limit=10"
    )
    memories = memories_response.json()
    
    # Get recent conversations
    conversations_response = requests.get(
        f"https://api-url/v1/mcp/conversations?uid={uid}&limit=5"
    )
    conversations = conversations_response.json()
    
    # Filter relevant context
    relevant_context = filter_relevant_memories(memories, current_topic)
    recent_patterns = analyze_conversation_patterns(conversations)
    
    return {
        'relevant_memories': relevant_context,
        'conversation_patterns': recent_patterns
    }

@router.post('/mcp-enhanced-advice', response_model=EndpointResponse)
async def mcp_enhanced_advice(data: RealtimePluginRequest):
    transcript = TranscriptSegment.segments_as_string(data.segments)
    uid = data.uid  # Assuming uid is available in request
    
    # Get MCP context
    mcp_context = await get_mcp_context(uid, transcript)
    
    # Generate personalized advice
    advice = generate_personalized_advice(
        transcript, 
        mcp_context['relevant_memories'],
        mcp_context['conversation_patterns']
    )
    
    return {'message': advice} if advice else {}
```

#### 6. Register and Deploy Plugin
```python
# Register in app manifest
app_config = {
    "id": "realtime-advisor",
    "name": "Real-time Conversation Advisor",
    "description": "Provides real-time advice during conversations",
    "triggers_on": "transcript_received",
    "webhook_url": "https://your-plugin-url.com/real-time-advice"
}
```

### Advanced Features

#### 1. Multi-modal Processing
- Access to conversation photos via `MemoryPhoto` model
- Integration with vision models for visual context
- Combined audio-visual analysis

#### 2. External Integrations
- **Webhooks**: Real-time notifications to external services
- **Actions**: Trigger external actions based on conversation content
- **OAuth**: Secure integration with third-party services

#### 3. Speech Profile Integration
- Access to user speech patterns
- Personalized advice based on communication style
- Speaker identification and analysis

#### 4. Proactive Notifications
- Context-aware suggestions
- Time-based reminders
- Location-based advice

## Key Development APIs

### Real-time WebSocket API
```
wss://api-url/v4/listen?language=en&sample_rate=8000&codec=pcm8&uid=user_id&include_speech_profile=true&stt_service=soniox
```

### Plugin Webhook Endpoints
- `POST /memory-created`: Triggered when conversation is processed
- `POST /realtime-transcript`: Triggered on real-time transcript segments
- `POST /day-summary`: Triggered on daily summaries

### OAuth 2.0 Integration API
```
GET /v1/oauth/authorize?app_id={app_id}&state={state}
POST /v1/oauth/callback
```

### Model Context Protocol (MCP) APIs
```python
# Memory Management
POST /v1/mcp/memories          # Create memory
GET /v1/mcp/memories           # List memories
PATCH /v1/mcp/memories/{id}    # Edit memory
DELETE /v1/mcp/memories/{id}   # Delete memory

# Conversation Access
GET /v1/mcp/conversations      # List conversations
GET /v1/mcp/conversations/{id} # Get specific conversation
```

### Vector Search API
```python
from database.vector_db import query_vectors_by_metadata

memories = query_vectors_by_metadata(
    uid=uid,
    vector=embedding,
    metadata_filters={'category': 'work'},
    k=10
)
```

## Latest Features and Updates

### Model Context Protocol (MCP) Integration
The Omi ecosystem now includes comprehensive MCP support, enabling:

- **Memory Management**: Create, read, update, and delete conversation memories
- **Conversation Access**: Retrieve and search through conversation history
- **External Tool Integration**: Connect Omi with other MCP-compatible tools
- **Claude Desktop Integration**: Direct integration with Anthropic's Claude Desktop
- **Multi-framework Support**: Examples for LangChain, DSPy, and OpenAI Agents SDK

```python
# Example MCP server usage
from mcp_server_omi.server import get_memories, get_conversations

# Access user memories
memories = await get_memories(uid="user_id", limit=100)

# Retrieve conversations
conversations = await get_conversations(uid="user_id", limit=25)
```

### Enhanced OAuth 2.0 System
- **Streamlined Authorization**: Visual OAuth flow with permission display
- **App Integration**: Secure third-party app connections
- **Capability Management**: Granular permission control for apps
- **User Experience**: Improved consent and authorization interface

### Improved LLM Processing
- **GPT-4.1 Integration**: Enhanced conversation processing with `llm_medium_experiment`
- **Multi-model Support**: Flexibility to choose optimal models for different tasks
- **Performance Optimization**: Better conversation structuring and summarization
- **Developer Tools**: Enhanced conversation prompt testing capabilities

### Firmware Testing & Development
- **Omi Shell Mode**: New testing firmware (`OMI_shell`) for development
- **OTA Updates**: Over-the-air firmware updates via nRF Connect
- **BLE Throughput Testing**: Performance monitoring tools
- **Enhanced Debugging**: Improved monitoring and logging capabilities

### Deepgram Enhancements
- **Autoscaling Improvements**: Better resource management for high-load scenarios
- **Self-hosted Support**: Option to use private Deepgram deployments
- **Model Selection**: Support for Nova-2 and Nova-3 models with automatic selection
- **Multi-language Optimization**: Enhanced language detection and processing

## Getting Started

1. **Device Setup**: Flash firmware to Omi device (including new Omi Shell for testing)
2. **App Installation**: Install Flutter app and connect device
3. **Plugin Development**: Create FastAPI-based plugins with OAuth support
4. **MCP Integration**: Connect with external tools via Model Context Protocol
5. **Knowledge Integration**: Use vector database for contextual responses
6. **Real-time Processing**: Implement WebSocket handlers for live transcription
7. **Deployment**: Deploy plugins and register in app marketplace

The Omi ecosystem provides a comprehensive platform for developing real-time AI-powered conversation applications with access to live transcription, knowledge bases, external integrations, and now enhanced connectivity through MCP and OAuth 2.0.