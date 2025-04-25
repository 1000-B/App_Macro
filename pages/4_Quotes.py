import streamlit as st
import pandas as pd
import random
from google.oauth2.service_account import Credentials
import gspread

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# Open sheet and read Quotes
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit#gid=2056045424"
spreadsheet = client.open_by_url(SHEET_URL)
quotes_sheet = spreadsheet.worksheet("Quotes")

# Load data into DataFrame
quotes_data = quotes_sheet.get_all_records()
quotes_df = pd.DataFrame(quotes_data)

st.title("📖 Daily Quotes & Mantras")

# Helper to show quote or mantra
def display_entry(entry, title):
    st.markdown(f"#### {title}")
    st.markdown(f"**Date**: {entry['Date']}  ")
    st.markdown(f"**Source**: {entry['Source']}  ")
    st.markdown(f"**Details1**: {entry['Details1']}  ")
    st.markdown(f"**Details2**: {entry['Details2']}  ")
    st.markdown("---")
    st.markdown(f"### *{entry['Quote']}*")
    st.markdown("---")

### SECTION 1: QUOTE
quote_candidates = quotes_df[quotes_df["Details1"] != "Mantras"]
if "quote_entry" not in st.session_state or st.button("📝 Display Another Quote"):
    st.session_state.quote_entry = quote_candidates.sample(1).iloc[0]

display_entry(st.session_state.quote_entry, "Today's Quote")

### SECTION 2: MANTRA
mantra_candidates = quotes_df[quotes_df["Details1"] == "Mantras"]
if "mantra_entry" not in st.session_state or st.button("🧘 Display Another Mantra"):
    st.session_state.mantra_entry = mantra_candidates.sample(1).iloc[0]

display_entry(st.session_state.mantra_entry, "Daily Mantra")
