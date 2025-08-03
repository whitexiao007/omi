# Real‑Time Audio & Transcription with OpenAI GPT‑4o Realtime

## 📦 Supported Models

| Model Alias                          | Category        | Notes                                                                                     |
|-------------------------------------|-----------------|------------------------------------------------------------------------------------------|
| `gpt‑4o‑realtime‑preview`           | full‑size       | Real‑time speech plus text + optional function‑calling                                   |
| `gpt‑4o‑mini‑realtime‑preview`      | lightweight     | Faster / cheaper real‑time model, lower latency                                          |
| `gpt‑4o‑transcribe`                 | transcription   | Superior real‑time STT model                                                             |
| `gpt‑4o‑mini‑transcribe`           | transcription   | Cheaper, faster version of `transcribe`                                                  |

## ⚙️ Requirements

- **Python 3.9+**
- Install dependencies:
```bash
pip install pyaudio websocket-client python-dotenv
```

- Environment Variables (`.env`):
```env
OPENAI_API_KEY=<your_openai_key>
# For Azure:
# AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
# AZURE_OPENAI_API_KEY=<your_azure_key>
# AZURE_OPENAI_DEPLOYMENT=gpt-4o-realtime-preview
```

## 🔗 API Endpoint

### OpenAI:
```
wss://api.openai.com/v1/realtime?api-version=2025-04-01-preview&deployment=<MODEL_ALIAS>&intent=transcription
```

### Azure:
```
wss://<your-resource>.openai.azure.com/openai/realtime?api-version=2025-04-01-preview&deployment=<DEPLOYMENT>
```

## 🧠 Session Configuration

```json
{
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
      "prompt": "Transcribe in English only.",
      "language": "en"
    }
  }
}
```

## 📜 Event Types

- `conversation.item.input_audio_transcription.delta`
- `conversation.item.input_audio_transcription.completed`
- `response.audio.delta`
- `response.text.delta`
- `response.done`

## 🧪 Sample Minimal Python Code

```python
import os, json, base64, time, threading
import websocket, pyaudio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
DEPLOYMENT = os.getenv("OPENAI_MODEL", "gpt-4o-transcribe")
URI = f"wss://api.openai.com/v1/realtime?api-version=2025-04-01-preview&deployment={DEPLOYMENT}&intent=transcription"

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
                "model": DEPLOYMENT,
                "language": "en"
            }
        }
    }))
    def stream_audio():
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=24000, input=True, frames_per_buffer=2400)
        while ws.keep_running:
            data = stream.read(2400, exception_on_overflow=False)
            b64 = base64.b64encode(data).decode()
            ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": b64}))
            time.sleep(0.1)
    threading.Thread(target=stream_audio).start()

def on_message(ws, msg):
    m = json.loads(msg)
    t = m.get("type", "")
    if t == "conversation.item.input_audio_transcription.delta":
        print(m.get("delta", ""), end="", flush=True)
    elif t == "conversation.item.input_audio_transcription.completed":
        print("\n✅ Final:", m.get("transcript"), "\n")

ws = websocket.WebSocketApp(
    URI,
    header={"Authorization": f"Bearer {API_KEY}"},
    on_open=on_open,
    on_message=on_message
)

ws.run_forever()
```

## 📚 References

- https://platform.openai.com/docs/guides/realtime
- https://platform.openai.com/docs/models/gpt-4o-realtime-preview
- https://learn.microsoft.com/en-us/azure/ai-foundry/openai/realtime-audio-quickstart