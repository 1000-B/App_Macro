import streamlit as st
import pandas as pd
import random
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

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
st.markdown(f"**Details:** {q['Details1']}, {q['Details2']}")
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
st.markdown(f"**Source Type:** {q['Source Type']}")
st.markdown(f"**Source:** {m['Source']}")
st.markdown(f"**Details:** {q['Details1']}, {q['Details2']}")
st.write(f"_{m['Quote']}_")

# Button to get a new random mantra
if st.button("Display Another Mantra"):
    st.session_state['mantra_random'] = mantras_df.sample(n=1).iloc[0]
    st.rerun()


