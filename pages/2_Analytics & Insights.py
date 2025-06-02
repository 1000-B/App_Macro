import openai
import os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

st.write("Loaded secret keys:", list(st.secrets.keys()))

st.title("📈 Analytics & Insights")

# Set your Groq API key (store it securely via Streamlit Secrets)
openai.api_key = st.secrets["GROQ_API_KEY"]
openai.api_base = "https://api.groq.com/openai/v1"

# Assuming 'df' is your food log DataFrame for the past 7–30 days
# --- Load Food Log ---
if 'log_data_full' not in st.session_state:
    st.error("No Food Log data found. Please log some food first.")
    st.stop()

food_log = st.session_state.log_data_full.copy()
food_log['Date'] = pd.to_datetime(food_log['Date'], dayfirst=True, errors='coerce')
food_log = food_log.dropna(subset=['Date'])
food_log = food_log.sort_values(by="Date", ascending=False)

summary_text = food_log.groupby('Date')[['Protein', 'Carbs', 'Fats', 'Calories']].sum().reset_index().to_string(index=False)
prompt = f"""
You are a macro tracking expert. Analyze the following food intake log and provide:
1. A summary of the user's overall macro intake.
2. Any visible trends or issues (e.g., low protein, high fat).
3. Suggestions for improving macro balance.

Food log:
{summary_text}
"""


# --- Timeframe Selection ---
st.subheader("Select Timeframe for Analysis")

today = datetime.today().date()
timeframe = st.radio("Choose a timeframe:", [
    "Today", "Yesterday", "Last 7 Days", "Last 14 Days",
    "Last 30 Days", "Last 90 Days", "Custom"
])

if timeframe == "Today":
    start_date = today
    end_date = today
elif timeframe == "Yesterday":
    start_date = today - timedelta(days=1)
    end_date = start_date
elif timeframe == "Last 7 Days":
    start_date = today - timedelta(days=6)
    end_date = today
elif timeframe == "Last 14 Days":
    start_date = today - timedelta(days=13)
    end_date = today
elif timeframe == "Last 30 Days":
    start_date = today - timedelta(days=29)
    end_date = today
elif timeframe == "Last 90 Days":
    start_date = today - timedelta(days=89)
    end_date = today
else:
    start_date = st.date_input("Start Date", today - timedelta(days=7))
    end_date = st.date_input("End Date", today)

# --- Filter Food Log by Date Range ---
mask = (food_log['Date'].dt.date >= start_date) & (food_log['Date'].dt.date <= end_date)
filtered_log = food_log[mask]

if filtered_log.empty:
    st.warning("No data in selected timeframe.")
    st.stop()

# --- Detailed Log String ---
display_cols = ['Date', 'Food', 'Quantity', 'Protein', 'Carbs', 'Fats', 'Calories']
food_log_str = filtered_log[display_cols].to_string(index=False)

# --- Daily Macro Summary ---
daily_summary = filtered_log.groupby('Date')[['Protein', 'Carbs', 'Fats', 'Calories']].sum().reset_index()
summary_str = daily_summary.to_string(index=False)


# --- Prompt Input & Generation ---
st.subheader("Nutrition Analysis by Llama 3")

default_prompt = f"""
You are an expert nutritionist. Analyze this food log for nutritional balance.
Look for patterns in protein intake, carb intake, excessive sugar or fats, and days with skipped meals.
The target is to gain muscle for someone who is approximately 69 kg and healthy.
Also, please analyze the food intake based on the food log provided, also at a micronutrient level, and provide what may be missing at both macro and micronutrient level.
Give actionable advice.

{food_log_str}

Here is a daily summary of total macros:

{summary_str}
"""

manual_prompt = st.text_area("🔍 Add an optional custom prompt for the AI (you can leave this blank):", "", height=150)

final_prompt = default_prompt + f"\n\nAdditional question:\n{manual_prompt}" if manual_prompt.strip() else default_prompt

if st.button("🧠 Analyze My Nutrition"):
    with st.spinner("Thinking..."):
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What's the weather like today?"}
                    ],
                temperature=0.7
            )
            ai_reply = response['choices'][0]['message']['content']
            st.markdown("### 📝 AI Response:")
            st.markdown(ai_reply)
        except Exception as e:
            st.error(f"Error calling Groq API: {e}")