import streamlit as st
import requests

# Set page config to add favicon and modify layout
st.set_page_config(page_title="University Service Chatbot", page_icon=":school:", layout="wide")

# Custom styles and theming
st.markdown("""
    <style>
        .big-font {
            font-size:20px !important;
        }
        .chatbox {
            border: 1px solid #e1e4e8;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #f0f0f0;
            align-self: flex-start;
        }
        .bot-message {
            background-color: #d6e5fa;
            align-self: flex-end;
        }
        .score {
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# Streamlit interface
st.title('University Service Chatbot :mortar_board:')
st.write('Ask questions about university services, courses, admissions, and more.')

# User input
user_input = st.text_input("Your question", "", max_chars=1000, help="Type your question and hit Enter.")
st.text("Example: What are the library opening hours?")

# Placeholder for chat messages
chat_placeholder = st.empty()

# When the user submits a question
if user_input:
    with chat_placeholder.container():
        # User's question
        st.markdown(f"<div class='chatbox user-message'>You: {user_input}</div>", unsafe_allow_html=True)
        
        # Simulate a spinner for the bot's response
        with st.spinner('🤖 Bot is thinking...'):
            # Prepare the request data
            request_data = {'question': user_input, 'top_n': 1}
            
            # URL of your FastAPI endpoint
            url = 'http://localhost:8000/search/'
            
            # POST request to the FastAPI server
            try:
                response = requests.post(url, json=request_data)
                response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP Error: {e.response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
            else:
                # Display bot's answer
                results = response.json().get('results', [])
                if results:
                    # Take the first result only
                    result = results[0]
                    st.markdown(f"<div class='chatbox bot-message'>Bot: {result['Content']} <a href='{result['URL']}' target='_blank'>Learn more</a></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chatbox bot-message'>Bot: No results found. Try rephrasing your question or check for typos.</div>", unsafe_allow_html=True)
            
            # Clear the input box after the question is sent
            st.session_state['user_input'] = ""

# Set the user_input key in the session state to an empty string on first run
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""
