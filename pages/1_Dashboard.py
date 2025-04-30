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

# Time Range first
st.sidebar.subheader("Time Range")
time_range = st.sidebar.selectbox("Select Range:", ["Week", "Month", "Quarter", "Year", "All"])

# Then Macro Selector
macro = st.sidebar.selectbox("Select Macro:", ['Protein', 'Carbs', 'Fats', 'Calories', 'All Macros'])

# Default threshold values
default_thresholds = {
    'Protein': (100, 150),
    'Carbs': (250, 400),
    'Fats': (50, 90),
    'Calories': (2000, 3000)
}

# Thresholds only applicable if not All Macros or Calories
if macro not in ['All Macros', 'Calories']:
    macro_min, macro_max = default_thresholds.get(macro, (0, 100))
    min_thresh = st.sidebar.number_input("Min Threshold", value=macro_min)
    max_thresh = st.sidebar.number_input("Max Threshold", value=macro_max)

# --- Time Range Filtering ---
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
mask = (food_log['Date'] >= start_date) & (food_log['Date'] <= end_date)
filtered_log = food_log[mask]

# Daily summary for plotting
filtered_macros = filtered_log.groupby('Date')[['Protein', 'Carbs', 'Fats', 'Calories']].sum().reset_index()

# --- Main Display ---
st.title("📈 Macro Intake Trends")
st.markdown(f"### {macro} Trends ({time_range})")

# --- Plotting ---
fig = go.Figure()

if macro == "All Macros":
    colors = {'Protein': 'blue', 'Carbs': 'orange', 'Fats': 'green'}
    for m in ['Protein', 'Carbs', 'Fats']:
        fig.add_trace(go.Scatter(
            x=filtered_macros['Date'],
            y=filtered_macros[m],
            mode='lines+markers',
            name=m,
            line=dict(color=colors[m])
        ))
else:
    color_map = {'Protein': 'blue', 'Carbs': 'orange', 'Fats': 'green', 'Calories': 'red'}
    fig.add_trace(go.Scatter(
        x=filtered_macros['Date'],
        y=filtered_macros[macro],
        mode='lines+markers',
        name=macro,
        line=dict(color=color_map.get(macro, 'blue'))
    ))

    # Threshold Band (only if not Calories)
    if macro != "Calories":
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
    yaxis_title="Grams" if macro != "Calories" else "Calories",
    title=f"{macro} Intake Over Time" if macro != "All Macros" else "Macro Intake Over Time",
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary Stats ---
if macro == "All Macros":
    totals = {m: filtered_macros[m].sum() for m in ['Protein', 'Carbs', 'Fats']}
    avg = {m: filtered_macros[m].mean() for m in ['Protein', 'Carbs', 'Fats']}
    days_tracked = filtered_macros['Date'].nunique()

    st.subheader(f"📌 Summary Stats — {days_tracked} Days Tracked")

    col1, col2, col3 = st.columns(3)
    col1.markdown("**Macro**")
    col2.markdown("**Total Intake (g)**")
    col3.markdown("**Avg Daily Intake (g)**")

    for m in ['Protein', 'Carbs', 'Fats']:
        col1.markdown(m)
        col2.markdown(f"{totals[m]:.1f}")
        col3.markdown(f"{avg[m]:.1f}")

else:
    st.subheader("📌 Summary Stats")

    total_macro = filtered_macros[macro].sum()
    avg_macro = filtered_macros[macro].mean()
    days_count = filtered_macros['Date'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Intake", f"{total_macro:.1f}")
    col2.metric("Average Daily Intake", f"{avg_macro:.1f}")
    col3.metric("Days Tracked", days_count)

    # --- Top 3 Foods for Selected Macro ---
    if macro in ['Protein', 'Carbs', 'Fats', 'Calories']:
        st.subheader(f"🍽️ Top 3 {macro} Sources")

        top_foods = (
            filtered_log.groupby('Food')[macro]
            .sum()
            .sort_values(ascending=False)
            .head(3)
            .reset_index()
        )

        for idx, row in top_foods.iterrows():
            st.markdown(f"{idx+1}. **{row['Food']}** — {row[macro]:.1f}")





