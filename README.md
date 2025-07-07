# Talk to Your LS Session

An AI-powered chat application that allows you to interact with your Livestorm session recordings. Upload a Livestorm session ID, and the app will transcribe the recording with speaker diarization, then let you ask questions about the content.

## Features

- **Livestorm Integration**: Direct processing of Livestorm session IDs
- **Advanced Transcription**: Uses ElevenLabs for high-quality transcription with speaker diarization
- **AI Chat Interface**: Ask questions about your session content using Google Gemini
- **Timing Information**: Get specific timestamps for when topics were mentioned
- **Content Generation**: Generate summaries, social media posts, follow-up emails, and blog posts
- **Speaker Detection**: Automatically identifies and tracks different speakers
- **Download Options**: Export chat history and transcriptions

## Quick Start

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   Create a `.env` file with:

   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   GEMINI_API_KEY=your_gemini_api_key
   LIVESTORM_API_KEY=your_livestorm_api_key
   ```

3. **Run the Application**

   ```bash
   streamlit run app.py
   ```

4. **Use the App**
   - Enter your Livestorm session ID
   - Wait for processing (download, transcription, diarization)
   - Start chatting with your session content!

## How It Works

1. **Session Processing**: The app fetches the replay URL from Livestorm API
2. **File Download**: Downloads the video file locally
3. **Transcription**: Uses ElevenLabs to transcribe with speaker diarization
4. **AI Setup**: Creates a vector database and AI chat system
5. **Interactive Chat**: Ask questions and get intelligent responses

## Key Features

### Timing Questions

Ask about when specific topics were mentioned:

- "When was prompt engineering discussed?"
- "At what time did they talk about foundation models?"

### Speaker-Based Queries

- "What did Speaker_1 say about AI?"
- "Who mentioned the most about machine learning?"

### Content Generation

- **Summaries**: One-paragraph comprehensive summaries
- **Social Media**: Platform-specific posts for LinkedIn, Facebook, Twitter
- **Follow-up Emails**: Professional email templates
- **Blog Posts**: Detailed blog content

### Advanced Features

- **Real-time Chat**: Messages appear immediately, AI responses follow
- **Full Transcript View**: Expandable transcript section
- **Download Options**: Export chat history and transcriptions
- **Speaker Statistics**: Automatic speaker detection and analysis

## File Structure

```
talk-to-vidz/
├── app.py                 # Main Streamlit application
├── livestorm_replay.py    # Livestorm session processing
├── transcriber.py         # ElevenLabs transcription
├── talker.py             # AI chat system
├── content_generator.py   # Content generation
├── prompts/              # AI prompt templates
│   ├── summary_prompt.txt
│   ├── email_prompt.txt
│   ├── social_media_prompt.txt
│   └── blog_prompt.txt
└── requirements.txt       # Python dependencies
```

## Dependencies

- **Streamlit**: Web application framework
- **ElevenLabs**: High-quality transcription and diarization
- **Google Gemini**: AI language model for chat and content generation
- **LangChain**: Vector database and AI orchestration
- **ElevenLabs**: Direct video/audio transcription
- **Requests**: HTTP requests for API calls

## API Keys Required

- **ElevenLabs API Key**: For transcription and diarization
- **Google Gemini API Key**: For AI chat and content generation
- **Livestorm API Key**: For accessing session replays

## Usage Examples

### Basic Questions

- "What was the main topic of this session?"
- "Summarize the key points discussed"
- "What questions did the audience ask?"

### Timing Questions

- "When did they start talking about AI?"
- "At what time was the Q&A session?"
- "When was the break mentioned?"

### Speaker Questions

- "What did the host say about the topic?"
- "Who spoke the most during the session?"
- "What did Speaker_2 contribute?"

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for internal use at Livestorm.
