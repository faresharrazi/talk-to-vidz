import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

load_dotenv()

def setup_qa_system(transcription_text):
    """
    Set up the Q&A system with the given transcription text
    
    Args:
        transcription_text (str): The transcribed text from the video
        
    Returns:
        tuple: (retriever, llm, prompt) for use in answering questions
    """
    # Split the transcription into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcription_text])
    
    # Create embeddings and vector store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Set up retriever
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
    )
    
    # Set up language model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0.2, 
        google_api_key=SecretStr(os.environ["GEMINI_API_KEY"])
    )
    
    # Set up prompt template
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

def ask_question(retriever, llm, prompt, question):
    """
    Ask a question about the video content
    
    Args:
        retriever: The retriever object
        llm: The language model object
        prompt: The prompt template
        question (str): The question to ask
        
    Returns:
        str: The answer to the question
    """
    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)
    
    # Combine retrieved content
    content_text = " ".join(doc.page_content for doc in retrieved_docs)
    
    # Format prompt and get response
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