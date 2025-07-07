import requests
import os
from dotenv import load_dotenv
import json
import tempfile
from transcriber import transcribe_video_with_diarization
from api_utils import get_api_key

load_dotenv()

def download_file_from_url(url, output_path=None):
    """
    Download a file from URL to local storage
    
    Args:
        url (str): URL to download from
        output_path (str, optional): Path to save the file. If None, creates temp file
        
    Returns:
        str: Path to the downloaded file
    """
    if output_path is None:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        output_path = temp_file.name
        temp_file.close()
    
    print(f"Downloading {url} to {output_path}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Download complete: {output_path}")
        return output_path
        
    except Exception as e:
        # Clean up the file if download failed
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise Exception(f"Failed to download file from {url}: {str(e)}")

def get_replay_url(session_id):
    """
    Get the replay URL for a Livestorm session
    
    Args:
        session_id (str): The Livestorm session ID
        
    Returns:
        str: The replay URL or error message
    """
    # Get API key from environment
    api_key = get_api_key("LS_API_KEY")
    if not api_key:
        return "Error: Livestorm API Key is required. Please add your API key in the sidebar settings."
    
    # API endpoint
    url = f"https://api.livestorm.co/v1/sessions/{session_id}?include=recordings"
    
    # Headers
    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": api_key
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Check if there are recordings
            if "included" in data and data["included"]:
                # Get the first recording URL
                recording = data["included"][0]
                if "attributes" in recording and "url" in recording["attributes"]:
                    replay_url = recording["attributes"]["url"]
                    return replay_url
                else:
                    return "Error: No URL found in recording data"
            else:
                return "Error: No recordings found for this session"
        else:
            return f"Error: API request failed with status code {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Error making API request: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error parsing API response: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def process_livestorm_session(session_id):
    """
    Complete workflow: Get replay URL, download file, and transcribe with diarization
    
    Args:
        session_id (str): The Livestorm session ID
        
    Returns:
        tuple: (transcription_text, diarization_data) or (None, error_message)
    """
    print(f"Processing Livestorm session: {session_id}")
    print("=" * 50)
    
    # Step 1: Get the replay URL
    print("1. Fetching replay URL...")
    replay_url = get_replay_url(session_id)
    
    if replay_url.startswith("Error:"):
        return None, replay_url
    
    print(f"✅ Replay URL found: {replay_url[:50]}...")
    
    # Step 2: Download the file
    print("\n2. Downloading file...")
    try:
        local_file_path = download_file_from_url(replay_url)
        print(f"✅ File downloaded: {local_file_path}")
    except Exception as e:
        return None, f"Error downloading file: {str(e)}"
    
    # Step 3: Transcribe the file
    print("\n3. Transcribing with diarization...")
    try:
        transcription_text, diarization_data = transcribe_video_with_diarization(local_file_path)
        print(f"✅ Transcription complete!")
        
        # Clean up the downloaded file
        if os.path.exists(local_file_path):
            os.unlink(local_file_path)
            print(f"✅ Cleaned up temporary file")
        
        return transcription_text, diarization_data
        
    except Exception as e:
        # Clean up the downloaded file on error
        if os.path.exists(local_file_path):
            os.unlink(local_file_path)
        return None, f"Error transcribing file: {str(e)}"

def main():
    """
    Main function to run the script interactively
    """
    print("Livestorm Session Processor")
    print("=" * 30)
    
    # Get session ID from user
    session_id = input("Enter the Livestorm Session ID: ").strip()
    
    if not session_id:
        print("Error: Session ID cannot be empty")
        return
    
    print(f"\nProcessing session: {session_id}")
    print("-" * 50)
    
    # Process the session
    result = process_livestorm_session(session_id)
    
    if result[0] is None:
        print(f"❌ {result[1]}")
    else:
        transcription_text, diarization_data = result
        print("✅ Processing complete!")
        print(f"\n📝 Transcription preview:")
        print(transcription_text[:200] + "..." if len(transcription_text) > 200 else transcription_text)
        
        if diarization_data and 'words' in diarization_data:
            speakers = set(word.speaker_id for word in diarization_data['words'] if hasattr(word, 'speaker_id') and word.speaker_id is not None)
            print(f"\n🎤 Speakers detected: {len(speakers)}")
            print(f"📊 Total words: {len(diarization_data['words'])}")
        
        print(f"\n💡 You can now use this data in your app!")

if __name__ == "__main__":
    main() 