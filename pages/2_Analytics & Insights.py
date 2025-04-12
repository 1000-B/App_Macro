import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Analytics & Insights")

if 'full_log_data' not in st.session_state:
    st.warning("No data available yet.")
else:
    log_data = pd.DataFrame(st.session_state['full_log_data'])
    if log_data.empty:
        st.warning("Log data is empty.")
    else:
        log_data["Date"] = pd.to_datetime(log_data["Date"])
        time_filter = st.radio("View by:", ("Daily", "Weekly", "Monthly"))

        def plot_macros(filtered_data):
            fig, ax = plt.subplots()
            filtered_data.set_index("Date")[['Protein', 'Carbs', 'Fats', 'Calories']].plot(kind='bar', ax=ax)
            st.pyplot(fig)

        if time_filter == "Daily":
            daily = log_data.groupby("Date", as_index=False).sum()
            plot_macros(daily)
        elif time_filter == "Weekly":
            log_data["Week"] = log_data["Date"].dt.to_period("W")
            weekly = log_data.groupby("Week", as_index=False).sum()
            plot_macros(weekly)
        elif time_filter == "Monthly":
            log_data["Month"] = log_data["Date"].dt.to_period("M")
            monthly = log_data.groupby("Month", as_index=False).sum()
            plot_macros(monthly)
