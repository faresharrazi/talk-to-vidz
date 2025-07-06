from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_youtube_transcript(video_id):
    """
    Get transcript from YouTube video using video ID
    
    Args:
        video_id (str): YouTube video ID (e.g., 'dQw4w9WgXcQ')
        
    Returns:
        str: Transcribed text from the video
    """
    try:
        # Get transcript list
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Extract text from transcript
        transcript_text = ""
        for transcript in transcript_list:
            transcript_text += transcript['text'] + " "
        
        return transcript_text.strip()
        
    except Exception as e:
        raise Exception(f"Error getting transcript: {str(e)}")

def extract_video_id(url):
    """
    Extract video ID from YouTube URL
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID
    """
    # Handle different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already a video ID
    return url

def transcribe_youtube_video(video_input):
    """
    Transcribe YouTube video from URL or video ID
    
    Args:
        video_input (str): YouTube URL or video ID
        
    Returns:
        str: Transcribed text
    """
    # Extract video ID
    video_id = extract_video_id(video_input)
    
    # Get transcript
    transcript = get_youtube_transcript(video_id)
    
    return transcript

# For testing
if __name__ == "__main__":
    # Test with a video ID
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll
    try:
        transcript = transcribe_youtube_video(test_video_id)
        print("Transcript:")
        print(transcript)
    except Exception as e:
        print(f"Error: {e}") 