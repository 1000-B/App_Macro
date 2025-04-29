import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Load Food Log ---
if 'log_data_full' not in st.session_state:
    st.error("No Food Log data found. Please log some food first.")
    st.stop()

food_log = st.session_state.log_data_full.copy()
food_log['Date'] = pd.to_datetime(food_log['Date'], dayfirst=True)

# Compute calories if not present
if 'Calories' not in food_log.columns:
    food_log['Calories'] = (
        food_log['Protein'] * 4 +
        food_log['Carbs'] * 4 +
        food_log['Fats'] * 9
    )

# --- Aggregate Daily Totals ---
daily_macros = food_log.groupby('Date')[['Protein', 'Carbs', 'Fats', 'Calories']].sum().reset_index()

# --- Sidebar Settings ---
st.sidebar.header("📊 Dashboard Settings")

macro = st.sidebar.selectbox("Select Macro:", ['Protein', 'Carbs', 'Fats', 'Calories'])

# Macro-based recommended default thresholds
default_thresholds = {
    'Protein': (120, 200),
    'Carbs': (250, 400),
    'Fats': (50, 90),
    'Calories': (2500, 3500)
}

macro_min, macro_max = default_thresholds.get(macro, (0, 100))

min_thresh = st.sidebar.number_input("Min Threshold", value=macro_min)
max_thresh = st.sidebar.number_input("Max Threshold", value=macro_max)


# Time Range Selection
st.sidebar.subheader("Time Range")
time_range = st.sidebar.selectbox("Select Range:", ["Week", "Month", "Quarter", "Year", "All"])

today = datetime.today()
if time_range == "Week":
    start_date = today - timedelta(days=6)
elif time_range == "Month":
    start_date = today.replace(day=1)
elif time_range == "Quarter":
    start_month = ((today.month - 1) // 3) * 3 + 1
    start_date = today.replace(month=start_month, day=1)
elif time_range == "Year":
    start_date = today.replace(month=1, day=1)
else:  # All
    start_date = daily_macros['Date'].min()

end_date = today
mask = (daily_macros['Date'] >= start_date) & (daily_macros['Date'] <= end_date)
filtered_macros = daily_macros[mask]

# --- Main Display ---
st.title("📈 Macro Intake Trends")
st.markdown(f"### {macro} Trends ({time_range})")

# --- Plot Line Chart with Thresholds ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtered_macros['Date'],
    y=filtered_macros[macro],
    mode='lines+markers',
    name=macro,
    line=dict(color='blue')
))

# Add threshold band
fig.add_shape(
    type="rect",
    x0=filtered_macros['Date'].min(),
    x1=filtered_macros['Date'].max(),
    y0=min_thresh,
    y1=max_thresh,
    fillcolor="green",
    opacity=0.2,
    layer="below",
    line_width=0,
)

fig.update_layout(
    height=450,
    margin=dict(l=30, r=30, t=50, b=40),
    xaxis_title="Date",
    yaxis_title=f"{macro} (g)" if macro != "Calories" else "Calories",
    title=f"{macro} Intake Over Time",
    yaxis=dict(range=[
        min(0, filtered_macros[macro].min() * 0.9),
        max(filtered_macros[macro].max() * 1.1, max_thresh * 1.05)
    ])
)


st.plotly_chart(fig, use_container_width=True)

# --- Summary Stats ---
st.subheader("📌 Summary Stats")

total_macro = filtered_macros[macro].sum()
avg_macro = filtered_macros[macro].mean()
days_count = filtered_macros['Date'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Intake", f"{total_macro:.1f}")
col2.metric("Average Daily Intake", f"{avg_macro:.1f}")
col3.metric("Days Tracked", days_count)
