import os
from dotenv import load_dotenv
from io import BytesIO
import requests
from elevenlabs.client import ElevenLabs

load_dotenv()

def transcribe_video(video_file_path):
    """
    Transcribe a video file using ElevenLabs API
    
    Args:
        video_file_path (str): Path to the video file
        
    Returns:
        str: Transcribed text
    """
    elevenlabs = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
    )

    # Read the video file
    with open(video_file_path, 'rb') as audio_file:
        audio_data = BytesIO(audio_file.read())

    transcription = elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",
        tag_audio_events=True,
        language_code="eng",
        diarize=True,
    )

    # Extract only the text from the transcription
    text_only = "".join([word.text for word in transcription.words])
    
    return text_only

# For testing the function directly
if __name__ == "__main__":
    result = transcribe_video("lamine.mp4")
    print("Pure transcript:")
    print(result)
