import streamlit as st
import pandas as pd
import random
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os


# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# Open the sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit#gid=2056045424"
spreadsheet = client.open_by_url(SHEET_URL)
bias_sheet = spreadsheet.worksheet("Bias")

# Load data into DataFrame
bias_df = pd.DataFrame(bias_sheet.get_all_records())

# Function to get a deterministic daily random row
def get_daily_random_row(df, seed_date):
    if df.empty:
        return None
    random.seed(seed_date.toordinal())
    return df.sample(n=1, random_state=random.randint(0, 100000)).iloc[0]

# --- Bias of the Day Section ---
st.subheader("🧠 Cognitive Bias of the Day")

# Check if we already have a random bias in session state
if 'bias_random' not in st.session_state:
    st.session_state['bias_random'] = get_daily_random_row(bias_df, date.today())

b = st.session_state['bias_random']

# Display the bias
st.markdown(f"**Date:** {b['Date']}")
st.markdown(f"**Phenomenon:** {b['Phenomenon']}")
st.markdown(f"**Area:** {b['Area']}")
st.markdown(f"**Bias:** {b['Bias']}")
st.markdown(f"**Definition:** {b['Definition']}")
st.markdown(f"**Localised Example:** {b['Localised Examples']}")

# Optional button to show another (non-deterministic) bias
if st.button("Display Another Bias"):
    st.session_state['bias_random'] = bias_df.sample(n=1).iloc[0]
    st.rerun()

