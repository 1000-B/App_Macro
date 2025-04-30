import streamlit as st
import pandas as pd
import random
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# Calculate the difference
birth_datetime = datetime(1981, 3, 8, 9, 20, 0)  # 8 March 1981, 09:20:00
now = datetime.now()
delta = now - birth_datetime

# Break down the delta
days = delta.days
seconds = delta.seconds
hours = seconds // 3600
minutes = (seconds % 3600) // 60
remaining_seconds = seconds % 60

# Display the message
st.markdown(f"### ⏳ {days} days, {hours} hours, {minutes} minutes, {remaining_seconds} seconds have passed since you were born.")
st.markdown("### 🌟 Relax and  make the most out of your time! Nothing is as serious as it seems! 😊")
st.markdown("---")


# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# Open the sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit#gid=2056045424"
spreadsheet = client.open_by_url(SHEET_URL)
quotes_sheet = spreadsheet.worksheet("Quotes")

# Load data
data = pd.DataFrame(quotes_sheet.get_all_records())

# Function to get a deterministic daily random row
def get_daily_random_row(df, seed_date):
    if df.empty:
        return None
    random.seed(seed_date.toordinal())
    return df.sample(n=1, random_state=random.randint(0, 100000)).iloc[0]

# --- Quotes Section ---
st.subheader("📜 Today's Quote")

quotes_df = data[data["Details1"].str.lower() != "mantras"]

# Check if we already have a random quote in session state
if 'quote_random' not in st.session_state:
    st.session_state['quote_random'] = get_daily_random_row(quotes_df, date.today())

q = st.session_state['quote_random']

# Display the current quote
st.markdown(f"**Date:** {q['Date']}")
st.markdown(f"**Source Type:** {q['Source Type']}")
st.markdown(f"**Source:** {q['Source']}")
st.markdown(f"**Details:** {q['Details1']}{', ' + q['Details2'] if q['Details2'] else ''}")
st.write(f"_{q['Quote']}_")

# Button to get a new random quote
if st.button("Display Another Quote"):
    st.session_state['quote_random'] = quotes_df.sample(n=1).iloc[0]
    st.rerun()


# --- Mantras Section ---
st.subheader("🧘‍♂️ Today's Mantra")

mantras_df = data[data["Details1"].str.lower() == "mantras"]

# Check if we already have a random mantra in session state
if 'mantra_random' not in st.session_state:
    st.session_state['mantra_random'] = get_daily_random_row(mantras_df, date.today())

m = st.session_state['mantra_random']

# Display the current mantra
st.markdown(f"**Date:** {m['Date']}")
st.markdown(f"**Source Type:** {m['Source Type']}")
st.markdown(f"**Source:** {m['Source']}")
st.markdown(f"**Details:** {m['Details1']}{', ' + m['Details2'] if m['Details2'] else ''}")
st.write(f"_{m['Quote']}_")

# Button to get a new random mantra
if st.button("Display Another Mantra"):
    st.session_state['mantra_random'] = mantras_df.sample(n=1).iloc[0]
    st.rerun()



# --- Daily Random Audio Clip Section ---
st.subheader("🎧 Today's Audio")

# Path to audio files in the deployed app
audio_dir = "audio_clips"

# List all audio files
audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))]

if audio_files:
    # Deterministically pick one per day
    seed = date.today().toordinal()
    random.seed(seed)
    audio_today = random.choice(audio_files)

    # Streamlit audio player
    audio_path = os.path.join(audio_dir, audio_today)
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3" if audio_today.endswith(".mp3") else "audio/wav")
        st.caption(f"Now playing: {audio_today}")
else:
    st.info("No audio files found.")



