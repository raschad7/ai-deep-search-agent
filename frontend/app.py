import streamlit as st
import requests


# CONFIGURATION
API_URL = "http://127.0.0.1:8000/api/deep_searcher"


st.set_page_config(page_title="Deep Search AI", page_icon="🌍", layout="centered")



if "messages" not in st.session_state:
    st.session_state.messages = []
    
    
def reset_conversation():
    """Clears the chat history."""
    st.session_state.messages = []
    
with st.sidebar:
    st.title("🎛️ Controls")
    if st.button(" New Search", use_container_width=True):
        reset_conversation()
        st.rerun()
    
    st.divider()
    
    # A toggle to show extra info (like if the bot decided to search or not)
    show_decision = st.toggle("Show Router Decision", value=True)
    
    st.markdown("### About")
    st.caption(
        "This AI decides intelligently whether to search the web "
        "or answer from internal knowledge."
    )
    

st.title("🌍 Deep Search Assistant")

#Display Chat History
# We check if there are messages, otherwise show a welcome note
if not st.session_state.messages:
    st.info("👋 Hello! Ask me anything (e.g., 'Latest news on AI', 'Who is Elon Musk?').")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Handle User Input
if prompt := st.chat_input("Ask a deep question..."):
    
    # A. Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("🧠 Thinking & Searching..."):
            try:
                # Prepare payload for FastAPI
                payload = {
                    "query": prompt,
                    "history": st.session_state.messages
                }
                
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["reply"]
                    decision = data["router_decision"]
                    
                    # Optional: Show the decision badge if toggle is ON
                    if show_decision:
                        if decision == "SEARCH":
                            st.caption("🌐 *Connected to the Web*")
                        else:
                            st.caption("🤖 *Internal Knowledge*")
                    
                    # Display the final answer (includes sources if backend sent them)
                    message_placeholder.markdown(answer)
                    
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                else:
                    message_placeholder.error(f"Server Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                message_placeholder.error("Could not connect to the Backend. Is it running?")