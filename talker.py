import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

load_dotenv()

def setup_qa_system(transcription_text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcription_text])
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0.2, 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    
    prompt = PromptTemplate(
        template="""
        You are a helpful AI assistant. Use the following pieces of context from a video transcription to answer the question at the end.
        If you don't know the answer based on the video content, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and relevant to the video content.
        
        Video Content: {context}
        Question: {question}
        """,
        input_variables=["context", "question"],
    )
    
    return retriever, llm, prompt

def setup_qa_system_with_diarization(transcription_text, diarization_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcription_text])
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0.2, 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    
    prompt = PromptTemplate(
        template="""
        You are a helpful AI assistant. Use the following pieces of context from a video transcription to answer the question at the end.
        If you don't know the answer based on the video content, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and relevant to the video content.
        
        IMPORTANT: You have access to detailed timing information for each word and speaker. When asked about timing, use the detailed timing data provided to give specific time ranges.
        
        Video Content: {context}
        
        Speaker Information: {speaker_info}
        
        Question: {question}
        """,
        input_variables=["context", "speaker_info", "question"],
    )
    
    speaker_info = ""
    if diarization_data and 'words' in diarization_data:
        speaker_stats = {}
        detailed_timing = []
        
        for word in diarization_data['words']:
            if hasattr(word, 'speaker_id') and word.speaker_id is not None:
                speaker_id = word.speaker_id
                if speaker_id not in speaker_stats:
                    speaker_stats[speaker_id] = {'count': 0, 'start_time': word.start, 'end_time': word.end}
                speaker_stats[speaker_id]['count'] += 1
                speaker_stats[speaker_id]['end_time'] = word.end
                
                if hasattr(word, 'text') and word.text:
                    detailed_timing.append({
                        'text': word.text,
                        'speaker': speaker_id,
                        'start_time': word.start,
                        'end_time': word.end
                    })
        
        if speaker_stats:
            speaker_info = "Speaker Analysis:\n"
            for speaker_id, stats in speaker_stats.items():
                duration = stats['end_time'] - stats['start_time']
                speaker_info += f"- {speaker_id}: {stats['count']} words, {duration:.1f} seconds\n"
            
            speaker_info += "\nDetailed Timing Information:\n"
            for item in detailed_timing:
                start_time = item['start_time']
                end_time = item['end_time']
                
                if start_time >= 60:
                    start_str = f"{start_time/60:.1f}m"
                else:
                    start_str = f"{start_time:.1f}s"
                    
                if end_time >= 60:
                    end_str = f"{end_time/60:.1f}m"
                else:
                    end_str = f"{end_time:.1f}s"
                
                speaker_info += f"- {start_str} to {end_str}: {item['speaker']} says '{item['text']}'\n"
    
    prompt = PromptTemplate(
        template="""
        You are a helpful AI assistant. Use the following pieces of context from a video transcription to answer the question at the end.
        If you don't know the answer based on the video content, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and relevant to the video content.
        
        IMPORTANT: You have access to detailed timing information for each word and speaker. When asked about timing, use the detailed timing data provided to give specific time ranges.
        
        Video Content: {context}
        
        Speaker Information: {speaker_info}
        
        Question: {question}
        """,
        input_variables=["context", "speaker_info", "question"],
    )
    
    class DiarizationRetriever:
        def __init__(self, base_retriever, speaker_info):
            self.base_retriever = base_retriever
            self.speaker_info = speaker_info
        
        def invoke(self, question):
            docs = self.base_retriever.invoke(question)
            if docs and self.speaker_info:
                docs[0].page_content += f"\n\n{self.speaker_info}"
            return docs
    
    enhanced_retriever = DiarizationRetriever(retriever, speaker_info)
    
    return enhanced_retriever, llm, prompt

def ask_question(retriever, llm, prompt, question):
    retrieved_docs = retriever.invoke(question)
    content_text = " ".join(doc.page_content for doc in retrieved_docs)
    
    if hasattr(prompt, 'input_variables') and 'speaker_info' in prompt.input_variables:
        speaker_info = ""
        if retrieved_docs and "Speaker Analysis:" in retrieved_docs[0].page_content:
            content_parts = retrieved_docs[0].page_content.split("Speaker Analysis:")
            if len(content_parts) > 1:
                content_text = content_parts[0].strip()
                speaker_info = "Speaker Analysis:" + content_parts[1]
        
        final_prompt = prompt.invoke({"context": content_text, "speaker_info": speaker_info, "question": question})
    else:
        final_prompt = prompt.invoke({"context": content_text, "question": question})
    
    response = llm.invoke(final_prompt)
    return response.content

# For testing the function directly
if __name__ == "__main__":
    # Test with sample transcription
    sample_transcription = "Hello, this is a test transcription."
    retriever, llm, prompt = setup_qa_system(sample_transcription)
    
    test_question = "What was said in the video?"
    answer = ask_question(retriever, llm, prompt, test_question)
    print(f"Question: {test_question}")
    print(f"Answer: {answer}")