import streamlit as st
import pandas as pd
from datetime import date
from streamlit_calendar import calendar

# 1. APP CONFIGURATION
st.set_page_config(page_title="My Personal CRM", layout="wide")

# 2. SESSION STATE MANAGEMENT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "theme_color" not in st.session_state:
    st.session_state.theme_color = "#1E90FF" # Default Blue
if "user_tasks" not in st.session_state:
    st.session_state.user_tasks = []

# --- DYNAMIC THEME INJECTION ---
# This applies the user's chosen color to buttons and highlights
st.markdown(f"""
    <style>
    div.stButton > button:first-child {{ background-color: {st.session_state.theme_color}; color: white; border: none; }}
    </style>
""", unsafe_allow_html=True)

# --- PAGE 1: THE LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("Welcome to your Personal CRM")
    st.markdown("Manage your life, business, and daily habits in one place.")
    
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Placeholder for actual Google OAuth
        if st.button("🔵 Continue with Google", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- PAGE 2: THE ONBOARDING QUESTIONNAIRE ---
if st.session_state.logged_in and not st.session_state.setup_complete:
    st.title("Let's build your system.")
    st.markdown("Select what you want to track. You can always add more later.")
    
    with st.form("setup_form"):
        # 1. App Aesthetics
        st.subheader("🎨 Choose Your App Accent Color")
        st.session_state.theme_color = st.color_picker("Pick a color", "#1E90FF")
        
        # 2. Lifestyle Dropdowns
        st.subheader("🏋️ Fitness & Health")
        health_goals = st.multiselect("Select tracking modules:", 
            ["Daily Water (1 Gal)", "Fasted Cardio", "Lifting Protocol", "Sleep Tracking", "Meal Prep"]
        )
        
        st.subheader("💼 Work & Business CRM")
        work_goals = st.multiselect("Select tracking modules:", 
            ["Lead Generation", "Client Follow-ups", "Admin Tasks", "Deep Work Blocks"]
        )
        
        st.subheader("📚 Learning & Growth")
        learn_goals = st.multiselect("Select tracking modules:", 
            ["Read 10 Pages", "Study/Coursework", "Skill Practice", "Journaling"]
        )
        
        st.subheader("🏡 Life & Household")
        life_goals = st.multiselect("Select tracking modules:", 
            ["Chores & Cleaning", "Pet Care", "Budgeting", "Groceries"]
        )
        
        submit = st.form_submit_button("Generate My Dashboard", use_container_width=True)
        
        if submit:
            # Consolidate all selections into the task database
            all_selections = health_goals + work_goals + learn_goals + life_goals
            for item in all_selections:
                st.session_state.user_tasks.append({"Task": item, "Status": "Pending"})
            
            st.session_state.setup_complete = True
            st.rerun()
    st.stop()

# --- PAGE 3: THE MAIN CRM & DASHBOARD ---
# Sidebar Navigation
st.sidebar.title("📱 My CRM")
page = st.sidebar.radio("Navigate:", ["🏠 Daily Board", "📅 Calendar Scheduler", "⚙️ Settings"])

if page == "🏠 Daily Board":
    st.title("Daily Action Board")
    st.caption(f"{date.today().strftime('%A, %B %d, %Y')}")
    
    st.subheader("Your Custom Targets")
    for idx, item in enumerate(st.session_state.user_tasks):
        if item["Status"] == "Pending":
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"◻️ {item['Task']}")
            with col2:
                if st.button("Done", key=f"btn_{idx}"):
                    st.session_state.user_tasks[idx]["Status"] = "Completed"
                    st.rerun()
        else:
            st.success(f"✅ ~{item['Task']}~")

elif page == "📅 Calendar Scheduler":
    st.title("Master Scheduler")
    st.markdown("Your 24-hour, weekly, and monthly view. *(Google Calendar Sync coming soon)*")
    
    # Configure the Calendar View
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay", # Month, Week, 24-Hour Day views
        },
        "initialView": "timeGridWeek", # Defaults to the weekly schedule
        "slotMinTime": "00:00:00", # Shows full 24 hours
        "slotMaxTime": "24:00:00",
    }
    
    # Example Events
    events = [
        {"title": "Deep Work Block", "start": f"{date.today()}T09:00:00", "end": f"{date.today()}T11:00:00", "color": st.session_state.theme_color},
        {"title": "Client Follow-ups", "start": f"{date.today()}T13:00:00", "end": f"{date.today()}T14:00:00", "color": "#FF4B4B"}
    ]
    
    calendar(events=events, options=calendar_options)

elif page == "⚙️ Settings":
    st.title("System Settings")
    st.write("Update your theme or reset your account.")
    new_color = st.color_picker("Change Accent Color", st.session_state.theme_color)
    if st.button("Save Color"):
        st.session_state.theme_color = new_color
        st.rerun()
    
    if st.button("Log Out & Reset App"):
        st.session_state.clear()
        st.rerun()
