import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from streamlit_calendar import calendar

st.set_page_config(page_title="Timeblock Journal", layout="wide")

# 1. LOCAL MEMORY (Temporary storage for testing)
if "events" not in st.session_state:
    st.session_state.events = []

# 2. THE 10-COLOR PALETTE
COLORS = {
    "🔴 Red (Urgent / Sales)": "#FF4B4B",
    "🟠 Orange (Operations)": "#FF9F36",
    "🟡 Yellow (Admin)": "#FFD700",
    "🟢 Green (Fitness / Diet)": "#00CC96",
    "🔵 Blue (Deep Work)": "#1E90FF",
    "🟣 Purple (Learning / Study)": "#8A2BE2",
    "💗 Pink (Household / Chores)": "#FF69B4",
    "🩵 Teal (Leisure / Family)": "#00CED1",
    "⚪ Gray (Sleep / Recovery)": "#A9A9A9",
    "⚫ Black (Non-Negotiable)": "#000000"
}

# 3. UI LAYOUT
st.title("📓 Daily Journal & Timeblocker")
st.markdown("Log your tasks, notes, and CRM updates. See your whole life at a glance.")

col1, col2 = st.columns([1, 3])

# --- LEFT COLUMN: THE CRM / JOURNAL ENTRY FORM ---
with col1:
    st.subheader("📝 New Entry")
    with st.form("new_event_form", clear_on_submit=True):
        task_name = st.text_input("Task / Event Title", placeholder="e.g., Studio Promo Outreach")
        selected_date = st.date_input("Date", date.today())
        
        # Time inputs set to 5-minute steps (300 seconds)
        c_start, c_end = st.columns(2)
        with c_start:
            start_time = st.time_input("Start Time", value=time(8, 0), step=300)
        with c_end:
            end_time = st.time_input("End Time", value=time(9, 0), step=300)
            
        color_choice = st.selectbox("Category Color", list(COLORS.keys()))
        
        # CRM / Journal aspect
        notes = st.text_area("Journal Notes / CRM Details", placeholder="Log notes, lead info, or workout details here...")
        
        if st.form_submit_button("Lock into Calendar", type="primary", use_container_width=True):
            if task_name:
                # Format timestamps for the calendar engine
                start_str = datetime.combine(selected_date, start_time).isoformat()
                end_str = datetime.combine(selected_date, end_time).isoformat()
                
                st.session_state.events.append({
                    "title": task_name,
                    "start": start_str,
                    "end": end_str,
                    "backgroundColor": COLORS[color_choice],
                    "borderColor": COLORS[color_choice],
                    "extendedProps": {"notes": notes}
                })
                st.success("Entry Saved!")
                st.rerun()

    # Mini daily ledger
    st.divider()
    st.subheader("Today's Journal")
    today_str = date.today().isoformat()
    todays_events = [e for e in st.session_state.events if e['start'].startswith(today_str)]
    
    if not todays_events:
        st.caption("No entries for today yet.")
    else:
        for e in todays_events:
            st.markdown(f"**{e['title']}**")
            if e['extendedProps']['notes']:
                st.caption(f"📝 {e['extendedProps']['notes']}")
            st.markdown("---")

# --- RIGHT COLUMN: THE MASTER CALENDAR ---
with col2:
    # We configure the calendar for 5-minute precision and 24-hour display
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth",
        },
        "initialView": "timeGridWeek",
        "slotDuration": "00:05:00", # Exactly 5-minute intervals
        "slotLabelInterval": "01:00", # Keeps the side labels at 1 hour so it's not cluttered
        "snapDuration": "00:05:00", # Events snap to 5 min marks
        "scrollTime": "06:00:00", # Auto-scrolls down to 6 AM when opened
        "height": "800px",
        "allDaySlot": False, # Hides the "all day" box to save space
    }
    
    calendar(events=st.session_state.events, options=calendar_options)
