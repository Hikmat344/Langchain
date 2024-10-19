from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import transformers
from transformers import LlamaForCausalLM, LlamaTokenizer
from transformers import AutoTokenizer
import torch

# Load the model and tokenizer
model = LlamaForCausalLM.from_pretrained("C:/Users/Alarab/Documents/New folder/Symptoms QA chatbot/lora_finetuned_model")
tokenizer = AutoTokenizer.from_pretrained("C:/Users/Alarab/Documents/New folder/Symptoms QA chatbot/lora_finetuned_model",
    use_fast=False,
    local_files_only=True,
)

def get_llama_response(input_text):
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")  # Use GPU if available
    with torch.no_grad():
        outputs = model.generate(inputs['input_ids'], max_length=150)  # Adjust max_length as needed
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Initialize Streamlit app
st.set_page_config(page_title="Symptoms Analysis Chatbot", layout="centered")

st.header("🩺 Symptoms Analysis Chatbot")

# Add basic styles to make it look like a messaging app
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
    .loading-icon {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-radius: 50%;
        border-top: 3px solid #3498db;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'bot_placeholder' not in st.session_state:
    st.session_state['bot_placeholder'] = None  # Placeholder for "Analyzing Input..."
if 'bot_response' not in st.session_state:
    st.session_state['bot_response'] = None

# Display chat history
for role, text, timestamp in st.session_state['chat_history']:
    if role == "You":
        st.markdown(f'<div class="chat-container"><div class="role">You</div><div class="user-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-container"><div class="role">Bot</div><div class="bot-message">{text}</div><div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)

# Fixed space for input field and button at the bottom
st.markdown("---")  # A separator line for visual separation

# Text input for custom questions at the bottom
input_container = st.container()  # Create a fixed container
with input_container:
    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)  # Start fixed bottom div
    input_text = st.text_input("Type symptoms you're feeling:", value="", key="input_text")  # Use a temporary variable
    submit = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)  # End fixed bottom div

# Handle sending the user input
if submit and input_text:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add user message to session chat history
    st.session_state['chat_history'].append(("You", input_text, now))

    # Show "Analyzing..." immediately in chat with bot and add loading icon
    st.session_state['bot_placeholder'] = ("Bot", '<div class="loading-icon"></div> Analyzing...', now)
    st.session_state['chat_history'].append(st.session_state['bot_placeholder'])

    # Get the response from the bot
    response = get_llama_response(input_text)

    # Process the response to show proper headings and line breaks
    formatted_response = ""
    for line in response.split('\n'):
        # Remove markdown asterisks and make relevant text bold
        if line.strip():
            line = line.replace('*', '').strip()  # Remove all asterisks
            if ':' in line:  # Check for headings with a colon
                heading, rest = line.split(':', 1)
                formatted_response += f"<strong>{heading.strip()}</strong>: {rest.strip()}<br>"  # Make heading bold
            else:
                formatted_response += line + "<br>"  # Add line breaks for other text

    # Remove the "Analyzing Input..." placeholder 
    st.session_state['chat_history'].pop()

    # Add the bot's actual response to the chat history
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['chat_history'].append(("Bot", formatted_response, now))

    # Clear the placeholder and update the bot's response
    st.session_state['bot_placeholder'] = None
    st.session_state['bot_response'] = formatted_response

# Display the bot's response
if st.session_state['bot_response']:
    st.markdown(f'<div class="chat-container"><div class="role">Bot</div><div class="bot-message">{st.session_state["bot_response"]}</div></div>', unsafe_allow_html=True)

# Automatically scroll to the bottom of the page when a new message is added
if st.session_state['chat_history']:
    st.markdown('<script>window.scrollTo(0, document.body.scrollHeight);</script>', unsafe_allow_html=True)