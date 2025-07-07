import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from api_utils import get_api_key

load_dotenv()

def setup_content_generator():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7,
        google_api_key=SecretStr(get_api_key("GEMINI_API_KEY"))
    )

def load_prompt(content_type):
    prompt_file = f"prompts/{content_type}_prompt.txt"
    
    if not os.path.exists(prompt_file):
        raise Exception(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as file:
        return file.read()

def generate_content(transcription_text, content_type):
    try:
        prompt_template = load_prompt(content_type)
        llm = setup_content_generator()
        full_prompt = f"{prompt_template}\n\n**Transcript:**\n{transcription_text}"
        response = llm.invoke(full_prompt)
        return response.content
        
    except Exception as e:
        raise Exception(f"Error generating {content_type} content: {str(e)}")

def generate_summary(transcription_text):
    return generate_content(transcription_text, "summary")

def generate_social_media_posts(transcription_text):
    return generate_content(transcription_text, "social_media")

def generate_email_template(transcription_text):
    return generate_content(transcription_text, "email")

def generate_blog_post(transcription_text):
    return generate_content(transcription_text, "blog")

# For testing
if __name__ == "__main__":
    # Test with sample transcription
    sample_transcription = "Hello, this is a test transcription for content generation."
    
    try:
        summary = generate_summary(sample_transcription)
        print("Summary generated successfully!")
        print(summary)
    except Exception as e:
        print(f"Error: {e}") 