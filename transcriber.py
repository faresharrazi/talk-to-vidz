import os
from dotenv import load_dotenv
from io import BytesIO
import requests
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip
import tempfile

load_dotenv()

def convert_video_to_mp3(video_path, output_path=None):
    """
    Convert MP4 video to MP3 audio using moviepy
    
    Args:
        video_path (str): Path to the video file
        output_path (str, optional): Path for output MP3. If None, creates temp file
        
    Returns:
        str: Path to the MP3 file
    """
    if output_path is None:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        output_path = temp_file.name
        temp_file.close()
    
    print(f"Converting {video_path} to {output_path}...")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_path)
    video.close()
    print(f"Conversion complete: {output_path}")
    return output_path

def transcribe_url_with_diarization(url):
    """
    Transcribe audio/video from URL with diarization using ElevenLabs
    
    Args:
        url (str): URL to the audio/video file
        
    Returns:
        tuple: (transcription_text, diarization_data)
    """
    elevenlabs = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
    )
    
    # Transcribe using cloud storage URL
    response = elevenlabs.speech_to_text.convert(
        cloud_storage_url=url,
        model_id="scribe_v1",
        tag_audio_events=True,
        language_code="eng",
        diarize=True
    )
    
    # Extract full text
    full_text = ""
    if hasattr(response, 'words'):
        for word in response.words:
            if hasattr(word, 'text') and word.text:
                full_text += word.text + " "
    
    # Clean up the text
    full_text = full_text.strip()
    
    # Convert response to dictionary for diarization data
    diarization_data = {
        'words': response.words if hasattr(response, 'words') else []
    }
    
    return full_text, diarization_data

def transcribe_url(url):
    """
    Transcribe audio/video from URL without diarization (backward compatibility)
    
    Args:
        url (str): URL to the audio/video file
        
    Returns:
        str: Transcription text
    """
    transcription_text, _ = transcribe_url_with_diarization(url)
    return transcription_text

def transcribe_video_with_diarization(video_file_path):
    """
    Transcribe video file with diarization (existing function for backward compatibility)
    
    Args:
        video_file_path (str): Path to the video file
        
    Returns:
        tuple: (transcription_text, diarization_data)
    """
    # Convert video to MP3
    mp3_path = convert_video_to_mp3(video_file_path)
    
    try:
        # Read the MP3 file
        with open(mp3_path, 'rb') as audio_file:
            audio_data = BytesIO(audio_file.read())
        
        # Transcribe with diarization
        elevenlabs = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        
        response = elevenlabs.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",
            tag_audio_events=True,
            language_code="eng",
            diarize=True
        )
        
        # Extract full text
        full_text = ""
        if hasattr(response, 'words'):
            for word in response.words:
                if hasattr(word, 'text') and word.text:
                    full_text += word.text + " "
        
        # Clean up the text
        full_text = full_text.strip()
        
        # Convert response to dictionary for diarization data
        diarization_data = {
            'words': response.words if hasattr(response, 'words') else []
        }
        
        return full_text, diarization_data
        
    finally:
        # Clean up temporary MP3 file
        if os.path.exists(mp3_path):
            os.unlink(mp3_path)

def transcribe_video(video_file_path):
    """
    Transcribe video file without diarization (existing function for backward compatibility)
    
    Args:
        video_file_path (str): Path to the video file
        
    Returns:
        str: Transcription text
    """
    transcription_text, _ = transcribe_video_with_diarization(video_file_path)
    return transcription_text

# For testing the functions directly
if __name__ == "__main__":
    # Test with a sample URL (you can replace this with an actual URL)
    test_url = "https://example.com/sample-audio.mp3"
    print("Testing URL transcription...")
    print(f"URL: {test_url}")
    
    try:
        text, diarization = transcribe_url_with_diarization(test_url)
        print(f"Transcription: {text}")
        print(f"Speakers detected: {len(set(word.speaker_id for word in diarization['words'] if hasattr(word, 'speaker_id') and word.speaker_id is not None))}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("This is expected if the URL doesn't point to a real audio file")
