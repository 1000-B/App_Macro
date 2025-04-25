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
st.header("💬 Today's Quote")

quotes_df = data[data["Details1"].str.lower() != "mantras"]
daily_quote = get_daily_random_row(quotes_df, date.today())

if daily_quote is not None:
    st.markdown(f"**Date:** {daily_quote['Date']}")
    st.markdown(f"**Source:** {daily_quote['Source']}")
    st.markdown(f"**Details1:** {daily_quote['Details1']}")
    st.markdown(f"**Details2:** {daily_quote['Details2']}")
    st.subheader("📜 Today's Quote")
    st.write(f"_{daily_quote['Quote']}_")

    if st.button("Display Another Quote"):
        st.session_state['quote_random'] = quotes_df.sample(n=1).iloc[0]

    if 'quote_random' in st.session_state:
        st.markdown("---")
        st.subheader("🔁 Another Random Quote")
        q = st.session_state['quote_random']
        st.markdown(f"**Date:** {q['Date']}")
        st.markdown(f"**Source:** {q['Source']}")
        st.markdown(f"**Details1:** {q['Details1']}")
        st.markdown(f"**Details2:** {q['Details2']}")
        st.write(f"_{q['Quote']}_")

# --- Mantras Section ---
st.header("🧘‍♂️ Today's Mantra")

mantras_df = data[data["Details1"].str.lower() == "mantras"]
daily_mantra = get_daily_random_row(mantras_df, date.today())

if daily_mantra is not None:
    st.markdown(f"**Date:** {daily_mantra['Date']}")
    st.markdown(f"**Source:** {daily_mantra['Source']}")
    st.markdown(f"**Details1:** {daily_mantra['Details1']}")
    st.markdown(f"**Details2:** {daily_mantra['Details2']}")
    st.subheader("📿 Today's Mantra")
    st.write(f"_{daily_mantra['Quote']}_")

    if st.button("Display Another Mantra"):
        st.session_state['mantra_random'] = mantras_df.sample(n=1).iloc[0]

    if 'mantra_random' in st.session_state:
        st.markdown("---")
        st.subheader("🔁 Another Random Mantra")
        m = st.session_state['mantra_random']
        st.markdown(f"**Date:** {m['Date']}")
        st.markdown(f"**Source:** {m['Source']}")
        st.markdown(f"**Details1:** {m['Details1']}")
        st.markdown(f"**Details2:** {m['Details2']}")
        st.write(f"_{m['Quote']}_")

