# import streamlit as st
# from PyPDF2 import PdfReader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import os
# from langchain_google_genai import GoogleGenerativeAIEmbeddings # we will use googe embiddings
# import google.generativeai as genai
# from langchain_community.vectorstores import FAISS # vectorstore
# from langchain_google_genai import ChatGoogleGenerativeAI 
# from langchain.chains.question_answering import load_qa_chain
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

# load_dotenv()
# os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# #read pdf
# def get_pdf_text(pdf_doc):
#     text=""
#     for pdf in pdf_doc:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text+=page.extract_text()
#     return text


# # convert pdf into chunks
# def get_text_chunks(text):
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
#     chunks = text_splitter.split_text(text)
#     return chunks
# #convert into vectors
# def get_vector_store(text_chunks):
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001") # embedding model from huggingface and its free
#     vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
#     vector_store.save_local("faiss_index") #im storing it in loca

# def get_conversational_chain():
#     prompt_template = """
#     Answer the question as detailed as possible from the provided context, make sure to provide all details, if the answer is not 
#     availabe in the provided context" , don't provide the wrong answer and say sorry there is no such information about that\n\n
#      context:\n{context}?\n
#      Question:\n{question}\n

#      Answer:
#     """

#     model=ChatGoogleGenerativeAI(model="gemini-pro" , temperature=0.3)

#     prompt = PromptTemplate(template=prompt_template, input_variables=["context","question"])
#     chain = load_qa_chain(model , chain_type="stuff", prompt=prompt)

#     return chain

# def user_input(user_query):
#     embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")

#     new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
#     docs = new_db.similarity_search(user_query)

#     chain = get_conversational_chain()

#     response = chain(
#         {"input_documents":docs, "question": user_query},
#         return_only_outputs=True
#     )

#     print(response)
#     st.write("reply: ", response["output_text"])


# def main():
#     st.set_page_config("Ask your PDFs")
#     st.header("Chat with your PDFs")

#     user_question = st.text_input("Ask any question from your PDFs")

#     if user_question:
#         user_input(user_question)

#     with st.sidebar:
#         st.title("Menu")
#         pdf_docs = st.file_uploader("Upload your PDF files" , type=['pdf'], accept_multiple_files=True)
#         if st.button("Submit & Process"):
#             if pdf_docs:
#                 with st.spinner("Processing..."):
#                     raw_text = get_pdf_text(pdf_docs)
#                     text_chunks = get_text_chunks(raw_text)
#                     get_vector_store(text_chunks)
#                     st.success("Done")
#             else:
#                 st.warning("Please upload PDF files before processing.")


# if __name__ == "__main__":
#     main()

#------------------------- 1 ----------------------------
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define a conversational chain for answering questions
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not available, say 
    "Sorry, no information is available on this topic in the context".\n\n
    Context:\n{context}?\n
    Question:\n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# Convert pdf text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Convert chunks into vector embeddings
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Read pdf function
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None returns
    return text

# Function to process user input and return bot response
def user_input(user_query):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_query)

        if not docs:
            return {"output_text": "Sorry, no relevant documents found."}  # Handle case with no results

        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_query}, return_only_outputs=True)
        
        return response
    except Exception as e:
        return {"output_text": f"Error processing your request: {str(e)}"}

# UI layout and styles for the chat interface
st.set_page_config(page_title="Ask your PDFs", layout="centered")
st.markdown("""
    <style>
    .chat-container {
        max-width: 600px;
        margin: 0 auto;
    }
    .user-message {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        text-align: left;
    }
    .bot-message {
        background-color: #E5E5EA;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        text-align: left;
        white-space: pre-wrap;
    }
    .role {
        font-weight: bold;
        margin-top: 10px;
    }
    .timestamp {
        font-size: 12px;
        color: gray;
        margin-bottom: 10px;
    }
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.2);
    }
    .chat-history {
        max-height: 80vh;  /* Limit height of chat history */
        overflow-y: auto;  /* Enable scrolling */
        margin-bottom: 60px;  /* Space for the input field */
    }
    .header {
        text-align: center;
        margin: 20px 0; /* Add margin for spacing */
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Centered header
st.markdown('<h1 class="header">📄 Chat with your PDFs</h1>', unsafe_allow_html=True)

# Sidebar for PDF uploads
with st.sidebar:
    st.title("Upload PDFs")
    pdf_docs = st.file_uploader("Upload your PDF files", type=['pdf'], accept_multiple_files=True)
    if st.button("Submit & Process"):
        if pdf_docs:
            with st.spinner("Processing..."):
                try:
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Processing complete! You can start asking questions.")
                except Exception as e:
                    st.error(f"Error processing PDF files: {e}")
        else:
            st.warning("Please upload PDF files before processing.")

# Display chat history
chat_history_container = st.container()
with chat_history_container:
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)  # Add scrollable container for chat history
    for role, text, timestamp in st.session_state['chat_history']:
        if role == "You":
            st.markdown(f'<div class="chat-container"><div class="role">You</div><div class="user-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-container"><div class="role">Bot</div><div class="bot-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close scrollable container

# Input field at the bottom for user question
input_container = st.container()
with input_container:
    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
    input_text = st.text_input("Ask your PDF a question:", value="", key="input_text")
    submit = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

# Handle user input and bot response
if submit and input_text:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['chat_history'].append(("You", input_text, now))
    
    # Display placeholder
    st.session_state['chat_history'].append(("Bot", "Analyzing Input...", now))

    # Get response from user_input function
    response = user_input(input_text)
    
    # Get the bot's response
    bot_response = response.get("output_text", "Sorry, something went wrong.")

    # Remove the placeholder and add bot response
    st.session_state['chat_history'][-1] = ("Bot", bot_response, now)  # Replace the last placeholder with the actual response

# Display the updated chat history again
with chat_history_container:
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)  # Add scrollable container for chat history
    for role, text, timestamp in st.session_state['chat_history']:
        if role == "You":
            st.markdown(f'<div class="chat-container"><div class="role">You</div><div class="user-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-container"><div class="role">Bot</div><div class="bot-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close scrollable container
