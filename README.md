# Talk to Video

A web app that transcribes videos and lets you chat with an AI about the content. Supports both uploaded video files and YouTube links.

## Features

- **Video Upload**: Upload video files (MP4, AVI, MOV, MKV)
- **YouTube Integration**: Paste YouTube URLs or video IDs
- **Automatic Transcription**: Uses ElevenLabs for file uploads, YouTube Transcript API for YouTube videos
- **AI Chat**: Chat with AI about video content using Google Gemini
- **Download Options**: Save transcriptions and chat history

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

### Upload Video Files

1. Go to "Upload File" tab
2. Select your video file
3. Click "Transcribe & Setup Chat"
4. Start asking questions about the video

### YouTube Videos

1. Go to "YouTube Link" tab
2. Paste YouTube URL or video ID
3. Click "Transcribe & Setup Chat"
4. Chat about the video content

## Supported Inputs

- **Video Files**: MP4, AVI, MOV, MKV
- **YouTube URLs**: Full links or video IDs
- **Example YouTube Input**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ` or `dQw4w9WgXcQ`

## Example Questions

- What is the main topic of this video?
- Who are the people mentioned in the video?
- What are the key points discussed?
- Can you summarize the video content?
