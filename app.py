import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from streamlit_calendar import calendar

st.set_page_config(page_title="Timeblock OS", layout="wide")

# --- 1. LOCAL MEMORY & DATABASE SIMULATION ---
if "users" not in st.session_state:
    st.session_state.users = {} # Stores profiles
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# We store data per-user now
def init_user_data(username):
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            "events": [],
            "tasks": [],
            "goals": []
        }

# --- 2. THE LOGIN & PROFILE GATEWAY ---
if st.session_state.current_user is None:
    st.title("Welcome to Life OS")
    st.markdown("Log in or create a profile to access your custom dashboard.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Create Profile")
        with st.form("register_form"):
            new_user = st.text_input("Choose a Username")
            if st.form_submit_button("Create Account", type="primary"):
                if new_user:
                    init_user_data(new_user)
                    st.session_state.current_user = new_user
                    st.success(f"Profile created! Welcome, {new_user}.")
                    st.rerun()
                    
    with col2:
        st.subheader("Existing Login")
        with st.form("login_form"):
            existing_user = st.text_input("Enter Username")
            if st.form_submit_button("Log In"):
                if existing_user in st.session_state.users:
                    st.session_state.current_user = existing_user
                    st.rerun()
                else:
                    st.error("User not found. Try creating a profile.")
    st.stop() # Stops the rest of the app from loading until logged in

# --- 3. MAIN APP (Only runs if logged in) ---
user = st.session_state.current_user
user_data = st.session_state.users[user]

st.sidebar.title(f"👤 {user}'s OS")
if st.sidebar.button("Log Out"):
    st.session_state.current_user = None
    st.rerun()

st.sidebar.divider()
page = st.sidebar.radio("Navigation", ["📅 Calendar & Journal", "✅ To-Do & Brain Dump", "🎯 Goals Tracker"])

COLORS = {
    "🔴 Urgent": "#FF4B4B", "🟠 Ops": "#FF9F36", "🟡 Admin": "#FFD700",
    "🟢 Fitness": "#00CC96", "🔵 Deep Work": "#1E90FF", "🟣 Study": "#8A2BE2",
    "⚪ Sleep/Rest": "#A9A9A9"
}

# --- PAGE 1: MASTER CALENDAR ---
if page == "📅 Calendar & Journal":
    st.title("Daily Journal & Timeblocker")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("📝 Schedule Event")
        with st.form("new_event_form", clear_on_submit=True):
            task_name = st.text_input("Event Title")
            selected_date = st.date_input("Date", date.today())
            
            c_start, c_end = st.columns(2)
            with c_start: start_time = st.time_input("Start", value=time(8, 0), step=300)
            with c_end: end_time = st.time_input("End", value=time(9, 0), step=300)
                
            color_choice = st.selectbox("Category Color", list(COLORS.keys()))
            notes = st.text_area("Journal Notes")
            
            if st.form_submit_button("Lock into Calendar", type="primary", use_container_width=True):
                if task_name:
                    start_str = datetime.combine(selected_date, start_time).isoformat()
                    end_str = datetime.combine(selected_date, end_time).isoformat()
                    user_data["events"].append({
                        "title": task_name, "start": start_str, "end": end_str,
                        "backgroundColor": COLORS[color_choice], "borderColor": COLORS[color_choice],
                    })
                    st.rerun()
    
    with col2:
        calendar_options = {
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "timeGridDay,timeGridWeek,dayGridMonth"},
            "initialView": "timeGridWeek",
            "slotDuration": "00:05:00",
            "snapDuration": "00:05:00",
            "scrollTime": "06:00:00",
            "height": "800px",
        }
        calendar(events=user_data["events"], options=calendar_options)

# --- PAGE 2: TO-DO & BRAIN DUMP ---
elif page == "✅ To-Do & Brain Dump":
    st.title("Task Manager & Inbox")
    st.markdown("Dump your thoughts here before they hit the calendar.")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("new_task"):
            new_t = st.text_input("Add a new task...")
            if st.form_submit_button("Add Task", type="primary"):
                if new_t:
                    user_data["tasks"].append({"Task": new_t, "Done": False})
                    st.rerun()
                    
    with col2:
        st.subheader("Active Tasks")
        if not user_data["tasks"]:
            st.caption("Inbox zero. Nice.")
        
        for idx, t in enumerate(user_data["tasks"]):
            if not t["Done"]:
                c1, c2 = st.columns([4, 1])
                c1.write(f"◻️ {t['Task']}")
                if c2.button("Done", key=f"t_{idx}"):
                    user_data["tasks"][idx]["Done"] = True
                    st.rerun()

# --- PAGE 3: GOALS TRACKER ---
elif page == "🎯 Goals Tracker":
    st.title("Macro Goals")
    
    with st.expander("➕ Add New Goal"):
        with st.form("new_goal"):
            g_name = st.text_input("Goal Title")
            g_target = st.number_input("Target Number (e.g., 100 leads, 30 workouts)", min_value=1, value=10)
            if st.form_submit_button("Create Goal", type="primary"):
                if g_name:
                    user_data["goals"].append({"Goal": g_name, "Current": 0, "Target": g_target})
                    st.rerun()

    st.divider()
    for idx, g in enumerate(user_data["goals"]):
        st.subheader(g["Goal"])
        # Visual Progress Bar
        progress = min(g["Current"] / g["Target"], 1.0)
        st.progress(progress)
        
        c1, c2 = st.columns(2)
        c1.write(f"**Progress:** {g['Current']} / {g['Target']}")
        with c2:
            if st.button("➕ Add +1 to Progress", key=f"g_{idx}"):
                user_data["goals"][idx]["Current"] += 1
                st.rerun()
