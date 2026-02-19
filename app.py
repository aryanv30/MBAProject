import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vedic AI Oracle", page_icon="🌌", layout="centered")
st.title("🌌 Vedic AI Oracle")
st.markdown("*Precision Faith-as-a-Service (FaaS) powered by Proprietary Knowledge.*")

# --- 2. LOAD PROPRIETARY DATASET ---
@st.cache_data
def load_dataset():
    try:
        # Looking for the exact CSV file you uploaded
        df = pd.read_csv("Complete_Astrology_DataSet.csv")
        return df
    except Exception as e:
        st.error(f"Dataset Error: {e}")
        return None

vedic_db = load_dataset()

# --- 3. TWO-STEP AI ARCHITECTURE ---

def get_gemini_chart_calculation(dob, tob, location, api_key):
    """Step 1: Ask Gemini to calculate the exact planetary positions."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    prompt = f"""
    You are a Vedic Astrology calculation engine.
    Calculate the current astrological placements for a person born on:
    Date: {dob}
    Time: {tob}
    Location: {location}
    
    You MUST respond with ONLY a raw JSON object. Do not add markdown blocks or explanations.
    The JSON must contain exactly these keys: "House" (integer 1-12), "Planet", "Mahadasha", "Antardasha", "Pratyanerdasha".
    The planets must be chosen from: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.
    
    Example output format:
    {{"House": 7, "Planet": "Venus", "Mahadasha": "Rahu", "Antardasha": "Jupiter", "Pratyanerdasha": "Saturn"}}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up the response in case Gemini adds ```json to the output
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        chart_data = json.loads(clean_json)
        return chart_data
    except Exception as e:
        # Fallback if the AI fails to generate proper JSON
        st.warning("Failed to calculate exact ephemeris. Using default planetary alignment.")
        return {"House": 1, "Planet": "Sun", "Mahadasha": "Sun", "Antardasha": "Sun", "Pratyanerdasha": "Moon"}

def fetch_proprietary_knowledge(chart_facts, df):
    """Step 2: Search the dataset using Gemini's calculated facts."""
    try:
        match = df[
            (df['House'] == int(chart_facts.get('House', 1))) & 
            (df['Planet'].str.contains(chart_facts.get('Planet', 'Sun'), case=False)) & 
            (df['Mahadasha'].str.contains(chart_facts.get('Mahadasha', 'Sun'), case=False)) & 
            (df['Antardasha'].str.contains(chart_facts.get('Antardasha', 'Sun'), case=False)) & 
            (df['Pratyanerdasha'].str.contains(chart_facts.get('Pratyanerdasha', 'Moon'), case=False))
        ]
        
        if not match.empty:
            effect = match.iloc[0]['Effect']
            remedies = match.iloc[0]['Remedies']
            return f"PROPRIETARY EFFECT: {effect}\nPROPRIETARY REMEDIES: {remedies}"
        else:
            return "No exact match in dataset. Use general Vedic principles."
    except Exception as e:
        return f"Database lookup error: {e}"

def generate_crisp_reading(user_name, user_question, chart_facts, proprietary_data, api_key):
    """Step 3: Final Synthesis with strict formatting rules."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    prompt = f"""
    You are an expert, direct Vedic Astrologer AI. Do not beat around the bush.
    
    USER: {user_name}
    QUESTION: {user_question}
    PLANETARY FACTS: {chart_facts}
    OUR DATABASE KNOWLEDGE: {proprietary_data}
    
    INSTRUCTIONS FOR YOUR RESPONSE:
    1. Directly answer the user's specific question based on the Database Knowledge.
    2. Write EXACTLY 8 crisp, precise lines explaining the situation and the astrological reason behind it.
    3. Then, leave one blank line.
    4. Provide EXACTLY 2 lines of clear, actionable remedies based on the Database Knowledge.
    5. Do NOT add any extra fluff, greetings, or closing statements.
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 4. USER INTERFACE ---
api_key = st.secrets.get("GOOGLE_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.markdown("### Enter Your Birth Details")
col1, col2, col3 = st.columns(3)
with col1:
    user_name = st.text_input("Name", "Seeker")
with col2:
    dob = st.date_input("Date of Birth")
with col3:
    # Changed to text_input so users can freely type "10:30 AM" or "02:15 PM"
    tob = st.text_input("Time of Birth (e.g., 10:30 AM)", "10:30 AM")

location = st.text_input("City of Birth", "New Delhi, India")
user_question = st.text_input("What specific guidance do you seek today?", "Will I find success in my career this year?")

if st.button("Generate My Vedic Reading"):
    if not api_key:
        st.error("Please enter your Gemini API Key.")
    elif vedic_db is None:
        st.error("Database not loaded.")
    else:
        with st.spinner("Step 1: Calculating planetary transits..."):
            time.sleep(1) # Pacing
            chart_facts = get_gemini_chart_calculation(dob, tob, location, api_key)
            
        with st.spinner("Step 2: Consulting the ancient texts..."):
            proprietary_data = fetch_proprietary_knowledge(chart_facts, vedic_db)
            
        with st.spinner("Step 3: Decoding your Karma..."):
            time.sleep(1) # Pacing
            final_reading = generate_crisp_reading(user_name, user_question, chart_facts, proprietary_data, api_key)
            
            # Display Results
            st.success("Reading Complete")
            st.markdown("---")
            st.markdown(final_reading)
            
            # MBA Project Proof (Expandable backend view)
            with st.expander("🔍 See FaaS Architecture (Backend Data)"):
                st.write("**1. Gemini Calculated these positions:**")
                st.json(chart_facts)
                st.write("**2. Python found this in the CSV Dataset:**")
                st.text(proprietary_data)
