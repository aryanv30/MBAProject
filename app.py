import streamlit as st
import google.generativeai as genai

# 1. Setup - Use your API Key here or via secrets
st.set_page_config(page_title="Celestial AI Astrologer", page_icon="✨")
st.title("✨ Celestial AI Astrologer")

# Sidebar for the API Key (good for testing)
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 2. The Astrologer's Personality (System Prompt)
    system_prompt = (
        "You are an expert, mystical AI Astrologer. Your tone is wise, poetic, and encouraging. "
        "Use astrological terms like 'Retrograde', 'Houses', 'Aspects', and 'Birth Chart'. "
        "If a user doesn't provide their Sun sign or birth date, ask for it politely. "
        "Always remind them that astrology is for guidance and entertainment."
    )

    # 3. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Ask the stars..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.info("Please enter your Gemini API Key in the sidebar to begin.")