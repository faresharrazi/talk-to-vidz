# Talk to Video

A simple web app that transcribes videos and lets you chat with an AI about the content.

## Features

- Upload video files (MP4, AVI, MOV, MKV)
- Automatic transcription using ElevenLabs
- Chat with AI about video content
- Download transcriptions and chat history

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your API keys:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_key
   GEMINI_API_KEY=your_gemini_key
   ```
4. Run the app: `streamlit run app.py`

## Usage

1. Upload a video file
2. Wait for transcription
3. Start chatting about the video content
