import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
from datetime import datetime

# --- 1. CONFIGURATION & MBA BRANDING ---
st.set_page_config(page_title="Vedic AI Oracle", page_icon="🌌", layout="centered")
st.title("🌌 Vedic AI Oracle")
st.markdown("*Precision Faith-as-a-Service (FaaS) powered by Proprietary Knowledge.*")

# --- 2. LOAD PROPRIETARY DATASET ---
@st.cache_data
def load_dataset():
    try:
        # Changed the filename to .zip and added the compression parameter
        df = pd.read_csv("Complete_Astrology_DataSet.zip", compression="zip")
        return df
    except Exception as e:
        st.error("Missing Complete_Astrology_DataSet.zip. Please upload it.")
        return None
        
vedic_db = load_dataset()

# --- 3. THE ASTROLOGY CALCULATION ENGINE ---
# In a production app, this function connects to a library like 'pyswisseph' or 'kerykeion'
# to calculate exact ephemeris data. For this prototype, we simulate the calculation engine.
def calculate_astrology_chart(dob, time, location):
    # SIMULATED CHART ENGINE: 
    # This represents the mathematically perfect calculation of the user's chart.
    # We pretend the math says the user is currently in a Sun Mahadasha, Sun Antardasha, etc.
    return {
        "House": 1,
        "Planet": "Sun",
        "Mahadasha": "Sun",
        "Antardasha": "Sun",
        "Pratyanerdasha": "Moon" # Using a specific combination from your CSV
    }

# --- 4. THE KNOWLEDGE RETRIEVAL SYSTEM ---
def fetch_proprietary_knowledge(chart_facts, df):
    # This looks up the exact P&C in your custom dataset
    try:
        match = df[
            (df['House'] == chart_facts['House']) & 
            (df['Planet'] == chart_facts['Planet']) & 
            (df['Mahadasha'] == chart_facts['Mahadasha']) & 
            (df['Antardasha'] == chart_facts['Antardasha']) & 
            (df['Pratyanerdasha'] == chart_facts['Pratyanerdasha'])
        ]
        
        if not match.empty:
            effect = match.iloc[0]['Effect']
            remedies = match.iloc[0]['Remedies']
            return f"PROPRIETARY EFFECT: {effect}\nPROPRIETARY REMEDIES: {remedies}"
        else:
            return "No proprietary data found for this specific micro-dasha. Rely on general Vedic texts."
    except Exception as e:
        return f"Database lookup error: {e}"

# --- 5. THE GEMINI SYNTHESIS PIPELINE ---
def generate_holistic_reading(user_name, user_question, chart_facts, proprietary_data, api_key):
    genai.configure(api_key=api_key)
    # Using Flash-Lite for high-speed, low-cost API tier
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    # This is the "System Prompt" that forces Gemini to combine everything
    prompt = f"""
    You are an expert, empathetic Vedic Astrologer AI.
    
    USER DETAILS:
    Name: {user_name}
    User's Question: {user_question}
    
    CALCULATED PLANETARY FACTS (Do not calculate yourself, use these as absolute truth):
    - Major Planet: {chart_facts['Planet']} in House {chart_facts['House']}
    - Current Dasha Period: {chart_facts['Mahadasha']} Mahadasha -> {chart_facts['Antardasha']} Antardasha -> {chart_facts['Pratyanerdasha']} Pratyanterdasha
    
    OUR PROPRIETARY VEDIC DATABASE RESULTS:
    {proprietary_data}
    
    YOUR TASK:
    1. Acknowledge the user's question empathetically.
    2. Explain their current planetary alignments (the Calculated Facts) in simple terms.
    3. Provide the exact predictions and remedies from the "PROPRIETARY VEDIC DATABASE RESULTS".
    4. Blend your deep astrological knowledge to explain *why* this remedy works.
    5. Keep the tone spiritual, supportive, and professional.
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 6. USER INTERFACE (STREAMLIT) ---
# Secrets Management
api_key = st.secrets.get("GOOGLE_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.markdown("### Enter Your Birth Details")
col1, col2, col3 = st.columns(3)
with col1:
    user_name = st.text_input("Name", "Seeker")
with col2:
    dob = st.date_input("Date of Birth", datetime(1995, 1, 1))
with col3:
    tob = st.time_input("Time of Birth", datetime.strptime("12:00", "%H:%M").time())

location = st.text_input("City of Birth", "New Delhi, India")
user_question = st.text_input("What guidance do you seek today?", "Will I find success in my career this year?")

if st.button("Generate My Vedic Reading"):
    if not api_key:
        st.error("Please enter your Gemini API Key.")
    elif vedic_db is None:
        st.error("Database not loaded.")
    else:
        with st.spinner("Calculating planetary transits & consulting the ancient texts..."):
            time.sleep(1) # Pacing for API limits
            
            # Step 1: Calculate the mathematical chart (Engine)
            chart_facts = calculate_astrology_chart(dob, tob, location)
            
            # Step 2: Fetch your proprietary predictions from CSV
            proprietary_data = fetch_proprietary_knowledge(chart_facts, vedic_db)
            
            # Step 3: Send everything to Gemini to write the beautiful response
            final_reading = generate_holistic_reading(user_name, user_question, chart_facts, proprietary_data, api_key)
            
            # Display Results
            st.success("Reading Complete")
            st.markdown("---")
            st.markdown(final_reading)
            
            # Displaying the "Under the Hood" facts for the MBA project presentation
            with st.expander("🔍 See FaaS Architecture (Backend Data)"):
                st.json(chart_facts)
                st.text(proprietary_data)

