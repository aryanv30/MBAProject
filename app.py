import streamlit as st
import google.generativeai as genai
import logging

# Setup standard logging for Streamlit Cloud logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Celestial AI 3.0", page_icon="🌌")
st.title("🌌 Celestial AI Astrologer")

# 1. Sidebar - API Configuration & Diagnostics
with st.sidebar:
    st.header("⚙️ System Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        
        # --- Diagnostic: List Available Models ---
        st.subheader("📡 Connection Status")
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name.replace('models/', ''))
            
            st.success("Connected to Google AI")
            st.write("**Available Models:**")
            st.code("\n".join(available_models))
            logger.info(f"Available models found: {available_models}")
        except Exception as e:
            st.error(f"Authentication Failed: {e}")

# 2. Main Logic
if api_key:
    # We use the 'latest' alias so your app stays updated automatically
    # As of Jan 2026, 'gemini-flash-latest' points to Gemini 3 Flash
    MODEL_ID = "gemini-2.5-flash" 
    
    try:
        model = genai.GenerativeModel(MODEL_ID)
        
        # Astrologer Personality
        system_prompt = (
            "You are a mystical AI Astrologer. Use poetic language and "
            "provide insights based on celestial movements."
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about your destiny..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Response Generation with Try/Catch
            with st.chat_message("assistant"):
                try:
                    full_prompt = f"{system_prompt}\n\nUser: {prompt}"
                    response = model.generate_content(full_prompt)
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.warning("The stars are silent. (Empty response from API)")
                        
                except Exception as e:
                    error_msg = f"Celestial Alignment Error: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"API Error: {e}")

    except Exception as e:
        st.error(f"Model Initialization Failed: {e}")
else:
    st.info("Please enter your API Key in the sidebar to begin your journey.")

