import streamlit as st
import google.generativeai as genai
import time

# --- INITIAL SETUP ---
st.set_page_config(page_title="Vedic Jyotish AI", page_icon="☸️", layout="centered")
st.title("☸️ Vedic Jyotish AI Astrologer")
st.markdown("*Seek guidance through the ancient wisdom of the Vedas.*")

# Secret-first approach: Check for API key in Streamlit Secrets OR manual input
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- VEDIC ASTROLOGY ENGINE ---
# We cache the function to prevent hitting the API quota on every page refresh
@st.cache_data(ttl=3600, show_spinner=False)
def get_vedic_reading(user_query, api_key):
    try:
        genai.configure(api_key=api_key)
        # Using 2.5-flash-lite for maximum free-tier reliability
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        system_prompt = (
            "You are a master of Indian Vedic Astrology (Jyotish). "
            "Your tone is traditional, humble, and deeply spiritual. "
            "Interpret all queries using concepts like: "
            "1. Rashis (Moon Signs) instead of Sun Signs. "
            "2. Nakshatras (Lunar Mansions). "
            "3. The 12 Bhavas (Houses) and their lords. "
            "4. Mahadashas (Planetary periods) and Sade Sati. "
            "If a user asks for a horoscope, ask for their Birth Date, Time, and Location (Panchang data). "
            "Always include a 'Remedy' (Upaya) like specific mantras or charitable acts."
        )
        
        full_prompt = f"{system_prompt}\n\nJataka (Seeker) Query: {user_query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- CHAT INTERFACE ---
if api_key:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if prompt := st.chat_input("Enter your birth details or ask about your Grahas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Calculating planetary transits..."):
                # Artificial delay to stay within 15 RPM free limit
                time.sleep(1) 
                response_text = get_vedic_reading(prompt, api_key)
                
                if "429" in response_text:
                    st.error("The stars are currently busy (Rate Limit). Please wait 60 seconds.")
                else:
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
else:
    st.warning("☸️ Please provide an API Key in the sidebar or Secrets to begin.")
