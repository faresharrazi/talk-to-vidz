import streamlit as st
import tempfile
import os
from transcriber import transcribe_video
from talker import setup_qa_system, ask_question

st.set_page_config(page_title="Talk to Video", layout="wide")

st.title("Talk to Video")
st.markdown("Upload a video and chat with AI about its content")

# Initialize session state
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = None
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for video upload
with st.sidebar:
    st.header("Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file", 
        type=['mp4', 'avi', 'mov', 'mkv']
    )
    
    if uploaded_file is not None:
        st.write(f"File: {uploaded_file.name}")
        st.write(f"Size: {uploaded_file.size / (1024*1024):.2f} MB")
        
        if st.button("Transcribe & Setup Chat", type="primary"):
            with st.spinner("Processing video..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Transcribe the video
                    transcription = transcribe_video(tmp_file_path)
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                    # Setup Q&A system
                    retriever, llm, prompt = setup_qa_system(transcription)
                    st.session_state.qa_system = (retriever, llm, prompt)
                    st.session_state.transcription = transcription
                    st.session_state.chat_history = []
                    
                    st.success("Video processed! You can now chat about it.")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Main chat interface
if st.session_state.qa_system is not None:
    st.header("Chat About Your Video")
    
    # Display transcription preview
    with st.expander("Video Transcription"):
        st.text_area("Transcription:", value=st.session_state.transcription, height=200, disabled=True)
    
    # Chat input
    user_question = st.chat_input("Ask a question about your video...")
    
    if user_question:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Get AI response
        with st.spinner("Thinking..."):
            try:
                retriever, llm, prompt = st.session_state.qa_system
                answer = ask_question(retriever, llm, prompt, user_question)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    # Download options
    if st.session_state.chat_history:
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Chat History",
                data="\n\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.chat_history]),
                file_name="chat_history.txt",
                mime="text/plain"
            )
        
        with col2:
            st.download_button(
                "Download Transcription",
                data=st.session_state.transcription,
                file_name="transcription.txt",
                mime="text/plain"
            )

else:
    st.info("Please upload a video file in the sidebar to get started")
    
    st.subheader("Example Questions:")
    st.markdown("""
    - What is the main topic of this video?
    - Who are the people mentioned in the video?
    - What are the key points discussed?
    - Can you summarize the video content?
    """) 