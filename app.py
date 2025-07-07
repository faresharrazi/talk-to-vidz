import streamlit as st
import tempfile
import os
from livestorm_replay import process_livestorm_session
from talker import setup_qa_system, ask_question, setup_qa_system_with_diarization
from content_generator import generate_summary, generate_social_media_posts, generate_email_template, generate_blog_post

st.set_page_config(page_title="Talk to Video", layout="wide")

# Main container
with st.container():
    st.markdown("<h1 style='text-align: center;'>Talk to your LS Session</h1>", unsafe_allow_html=True)

# Initialize session state
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = None
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'diarization_data' not in st.session_state:
    st.session_state.diarization_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'video_source' not in st.session_state:
    st.session_state.video_source = ""

# Main input area
if st.session_state.qa_system is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        session_id_input = st.text_input(
            "Session ID",
            placeholder="04a6e7e0-85f9-41b6-8fa1-bfe530923c40",
            label_visibility="collapsed"
        )
        
        if st.button("Let's Chat", type="primary", use_container_width=True):
            if session_id_input:
                with st.spinner("Processing..."):
                    try:
                        result = process_livestorm_session(session_id_input)
                        
                        if result[0] is None:
                            st.error(f"Error: {result[1]}")
                        else:
                            transcription, diarization_data = result
                            
                            retriever, llm, prompt = setup_qa_system_with_diarization(transcription, diarization_data)
                            st.session_state.qa_system = (retriever, llm, prompt)
                            st.session_state.transcription = transcription
                            st.session_state.diarization_data = diarization_data
                            st.session_state.chat_history = []
                            st.session_state.video_source = f"Session: {session_id_input}"
                            
                            if diarization_data and 'words' in diarization_data:
                                speakers = set(word.speaker_id for word in diarization_data['words'] if hasattr(word, 'speaker_id') and word.speaker_id is not None)
                                if len(speakers) > 0:
                                    st.success(f"✅ Ready! {len(speakers)} speakers detected.")
                                else:
                                    st.success("✅ Ready!")
                            else:
                                st.success("✅ Ready!")
                            
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Please enter a Session ID")

# Main chat interface
if st.session_state.qa_system is not None:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.session_state.video_source:
            st.info(f"Source: {st.session_state.video_source}")
    
    with col2:
        if st.button("🔄 New Session", type="secondary"):
            st.session_state.qa_system = None
            st.session_state.transcription = ""
            st.session_state.diarization_data = None
            st.session_state.chat_history = []
            st.session_state.video_source = ""
            st.rerun()
    
    if st.session_state.diarization_data and 'words' in st.session_state.diarization_data:
        speakers = set(word.speaker_id for word in st.session_state.diarization_data['words'] if hasattr(word, 'speaker_id') and word.speaker_id is not None)
        if len(speakers) > 0:
            st.write(f"🎤 {len(speakers)} speakers detected")
    
    with st.expander("📄 Full Transcript", expanded=False):
        st.text_area("Transcription", value=st.session_state.transcription, height=300, disabled=True)
    
    user_question = st.chat_input("Ask a question about your video...")
    
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        st.subheader("Chat History")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
        
        with st.spinner("Thinking..."):
            try:
                retriever, llm, prompt = st.session_state.qa_system
                answer = ask_question(retriever, llm, prompt, user_question)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                st.rerun()
    else:
        if st.session_state.chat_history:
            st.subheader("Chat History")
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
    
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Summarize", type="secondary", use_container_width=True):
            with st.spinner("Generating content..."):
                try:
                    summary = generate_summary(st.session_state.transcription)
                    st.session_state.chat_history.append({"role": "user", "content": "Generate a summary"})
                    st.session_state.chat_history.append({"role": "assistant", "content": summary})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
    
    with col2:
        if st.button("📱 Social Media", type="secondary", use_container_width=True):
            with st.spinner("Generating content..."):
                try:
                    social_posts = generate_social_media_posts(st.session_state.transcription)
                    st.session_state.chat_history.append({"role": "user", "content": "Generate social media posts"})
                    st.session_state.chat_history.append({"role": "assistant", "content": social_posts})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating social media posts: {str(e)}")
    
    with col3:
        if st.button("📧 Follow-up Email", type="secondary", use_container_width=True):
            with st.spinner("Generating content..."):
                try:
                    email_template = generate_email_template(st.session_state.transcription)
                    st.session_state.chat_history.append({"role": "user", "content": "Generate follow-up email"})
                    st.session_state.chat_history.append({"role": "assistant", "content": email_template})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating email template: {str(e)}")
    
    with col4:
        if st.button("📄 Blog Post", type="secondary", use_container_width=True):
            with st.spinner("Generating content..."):
                try:
                    blog_post = generate_blog_post(st.session_state.transcription)
                    st.session_state.chat_history.append({"role": "user", "content": "Generate blog post"})
                    st.session_state.chat_history.append({"role": "assistant", "content": blog_post})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating blog post: {str(e)}")
    
    if st.session_state.chat_history:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "📥 Download Chat History",
                data="\n\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.chat_history]),
                file_name="chat_history.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                "📥 Download Transcription",
                data=st.session_state.transcription,
                file_name="transcription.txt",
                mime="text/plain",
                use_container_width=True
            ) 