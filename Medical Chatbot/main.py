from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# function to load genini pro and get response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# To initialize our streamlit app
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
    .heading {
        font-weight: bold;
        margin-top: 10px;
        font-size: 16px;  /* Adjust the size of headings */
        color: #333;
    }
    .fixed-bottom {
        position: fixed;
        bottom: 0;  /* Stick to the bottom */
        left: 0;
        right: 0;   /* Span the full width */
        background-color: white;  /* Optional: background color */
        padding: 10px;  /* Add some padding */
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.2);  /* Optional: add shadow for separation */
    }
    </style>
    """, unsafe_allow_html=True)

# To Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'bot_placeholder' not in st.session_state:
    st.session_state['bot_placeholder'] = None  # Placeholder for "Analyzing Input..."

# Add a container for the chat history
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
    input_text = st.text_input("Type symptoms you are feeling: ", value="", key="input_text")  # Use a temporary variable
    submit = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)  # End fixed bottom div

# To Handle sending the user input
if submit and input_text:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add user message to session chat history
    st.session_state['chat_history'].append(("You", input_text, now))
    
    # Immediately show "Analyzing Input..." in the chat history
    st.session_state['bot_placeholder'] = ("Bot", "Analyzing Input...", now)
    st.session_state['chat_history'].append(st.session_state['bot_placeholder'])

    # Rerun to show the user message and placeholder
    st.experimental_rerun()

# To Handle bot response asynchronously after showing the placeholder
if st.session_state['bot_placeholder'] and st.session_state['bot_placeholder'][1] == "Analyzing Input...":
    # Get the response from the bot
    response = get_gemini_response(input_text)
    
    # Stream bot's response
    bot_response = ""
    for chunk in response:
        bot_response += chunk.text

    # to Process the response to show proper headings and line breaks
    formatted_response = ""
    for line in bot_response.split('\n'):
        # to Remove markdown asterisks and make relevant text bold
        if line.strip():
            line = line.replace('*', '').strip()  # Remove all asterisks
            if ':' in line:  # Check for headings with a colon
                heading, rest = line.split(':', 1)
                formatted_response += f"<strong>{heading.strip()}</strong>: {rest.strip()}<br>"  # Make heading bold
            else:
                formatted_response += line + "<br>"  # Add line breaks for other text

    # to Remove the "Analyzing Input..." placeholder
    st.session_state['chat_history'].pop()

    # to Add the bot's actual response to the chat history
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['chat_history'].append(("Bot", formatted_response, now))

    # To Clear the placeholder and rerun to display the bot's response
    st.session_state['bot_placeholder'] = None
    st.experimental_rerun()
