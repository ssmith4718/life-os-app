import streamlit as st
from datetime import datetime, date, time, timedelta
import re
from streamlit_calendar import calendar

st.set_page_config(page_title="Universal Life OS", layout="wide")

# --- 1. LOCAL MEMORY & DATABASE ---
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def init_user_data(username, password):
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            "password": password,
            "setup_complete": False,
            "wake_up": time(6, 0),
            "events": [],
            "tasks": [],
            "goals": []
        }

# --- 2. AUTHENTICATION GATEWAY ---
if st.session_state.current_user is None:
    st.title("Life OS")
    st.markdown("Log in or create an account to access your universal command center.")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("New Account")
            with st.form("register_form"):
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account", type="primary"):
                    if new_user and new_pass:
                        if new_user in st.session_state.users:
                            st.error("Username taken.")
                        else:
                            init_user_data(new_user, new_pass)
                            st.session_state.current_user = new_user
                            st.rerun()
                    else:
                        st.error("Please enter a username and password.")
                        
    with col2:
        with st.container(border=True):
            st.subheader("Log In")
            with st.form("login_form"):
                existing_user = st.text_input("Username")
                existing_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Log In"):
                    if existing_user in st.session_state.users and st.session_state.users[existing_user]["password"] == existing_pass:
                        st.session_state.current_user = existing_user
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
    st.stop()

# --- 3. CURRENT USER CONTEXT ---
user = st.session_state.current_user
user_data = st.session_state.users[user]

st.sidebar.title(f"👤 {user}")
if st.sidebar.button("Log Out"):
    st.session_state.current_user = None
    st.rerun()

# --- 4. THE UNIVERSAL ONBOARDING QUESTIONNAIRE ---
if not user_data["setup_complete"]:
    st.title("Build Your Operating System. 🚀")
    st.markdown("Select your habits and targets, or create your own.")
    
    with st.form("setup_questionnaire"):
        st.subheader("1. Daily Anchor")
        wake_time = st.time_input("What time do you usually wake up?", value=time(6, 0))
        
        st.subheader("2. Professional KPIs & Macro Goals")
        biz_goals = st.multiselect("Select your core objectives:", [
            # Sales & Growth
            "Sales: Close 5 New Deals Weekly", "Growth: Generate 20 Qualified Leads", "Finance: Increase Revenue by 15%", "Networking: Send 10 Cold Connections",
            # Ops & Management
            "Ops: Achieve 90% Task Completion", "Admin: Zero Inbox Daily", "Management: Weekly Team 1-on-1s", "Finance: Review Weekly Cash Flow",
            # Freelance, Creative & Tech
            "Content: Publish 3 Pieces Weekly", "Freelance: Secure 2 New Client Retainers", "Productivity: 4 Hours of Deep Work", 
            "Tech: Commit Code Daily", "Tech: 1 Hour of Technical Upskilling", "Tech: Squash 5 Bugs Weekly",
            # Academic / Learning
            "Study: 3 Hours of Focused Study", "Academic: Read 2 Research Papers", "Academic: Attend All Lectures"
        ])
        
        # The Custom Goal Engine
        custom_goal = st.text_input("➕ Add a Custom Goal (e.g., 'Book 10 Podcast Interviews')")
        
        st.subheader("3. Personal & Fitness Routines")
        routines = st.multiselect("Select daily routines to auto-schedule:", [
            # Fitness
            "Strength Training / Gym (45 mins)", "Zone 2 Cardio / Running (30 mins)", "HIIT Workout (20 mins)", 
            "Yoga & Mobility (20 mins)", "Daily 10k Steps", "Pilates / Core Work (30 mins)",
            # Health & Diet
            "Hydration: Drink 1 Gallon of Water", "Meal Prep & Nutrition Logging", "Strict 8-Hour Sleep Block",
            "Take Vitamins/Supplements", "Intermittent Fasting Window", "Cook Dinner at Home",
            # Mindset & Learning
            "Read 15 Pages of Non-Fiction", "10-Minute Mindfulness / Meditation", "Listen to Industry Podcast",
            "Journaling / Brain Dump", "Learn a Language (15 mins)", "Practice an Instrument",
            # Life Admin & Household
            "Household Chores / Deep Clean", "Screen-Free Wind Down", "Family / Relationship Time",
            "Water Plants / Gardening", "Review Personal Budget", "Creative Hobby Block"
        ])
        
        # The Custom Routine Engine
        st.markdown("**➕ Add a Custom Routine**")
        colA, colB = st.columns([3, 1])
        with colA: custom_routine = st.text_input("Routine Name (e.g., 'Walk the Dog', 'Review F1 News')")
        with colB: custom_routine_time = st.time_input("Time of day", value=time(12, 0))
        
        if st.form_submit_button("Generate My Dashboard", type="primary", use_container_width=True):
            user_data["wake_up"] = wake_time
            
            # Combine pre-built and custom goals
            all_goals = biz_goals.copy()
            if custom_goal: all_goals.append(custom_goal)
            
            # Extract numbers for goal targets
            for goal in all_goals:
                match = re.search(r'\d+', goal)
                target_num = int(match.group()) if match else 10
                clean_name = goal.split(":")[1].strip() if ":" in goal else goal
                user_data["goals"].append({"Goal": clean_name, "Current": 0, "Target": target_num})
            
            # Auto-populate the calendar
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            
            for i in range(7):
                day = start_of_week + timedelta(days=i)
                wake_dt = datetime.combine(day, wake_time)
                
                # Wake Up Block
                user_data["events"].append({
                    "title": "🌅 Wake Up", "start": wake_dt.isoformat(), 
                    "end": (wake_dt + timedelta(minutes=15)).isoformat(), "backgroundColor": "#FFD700"
                })
                
                # Dynamic Routing for a few key visual anchors
                if "10-Minute Mindfulness / Meditation" in routines:
                    med_dt = wake_dt + timedelta(minutes=15)
                    user_data["events"].append({"title": "🧘 Mindfulness", "start": med_dt.isoformat(), "end": (med_dt + timedelta(minutes=10)).isoformat(), "backgroundColor": "#00CED1"})
                if "Strength Training / Gym (45 mins)" in routines:
                    lift_dt = datetime.combine(day, time(17, 0)) 
                    user_data["events"].append({"title": "🏋️ Strength Training", "start": lift_dt.isoformat(), "end": (lift_dt + timedelta(minutes=45)).isoformat(), "backgroundColor": "#FF4B4B"})
                if "Read 15 Pages of Non-Fiction" in routines:
                    read_dt = datetime.combine(day, time(20, 0)) 
                    user_data["events"].append({"title": "📚 Reading", "start": read_dt.isoformat(), "end": (read_dt + timedelta(minutes=30)).isoformat(), "backgroundColor": "#8A2BE2"})
                if "Screen-Free Wind Down" in routines:
                    wind_dt = datetime.combine(day, time(21, 30)) 
                    user_data["events"].append({"title": "🌙 Wind Down", "start": wind_dt.isoformat(), "end": (wind_dt + timedelta(minutes=30)).isoformat(), "backgroundColor": "#A9A9A9"})
                
                # Inject Custom Routine
                if custom_routine:
                    custom_dt = datetime.combine(day, custom_routine_time)
                    user_data["events"].append({
                        "title": f"✨ {custom_routine}", "start": custom_dt.isoformat(), 
                        "end": (custom_dt + timedelta(minutes=30)).isoformat(), "backgroundColor": "#FF9F36"
                    })

            user_data["setup_complete"] = True
            st.balloons()
            st.rerun()
    st.stop()

# --- 5. MAIN DASHBOARD ---
st.sidebar.caption(f"Wake Time: {user_data['wake_up'].strftime('%I:%M %p')}")

st.title("Command Center")
col_left, col_right = st.columns([1, 2.5])

with col_left:
    with st.container(border=True):
        st.subheader("✅ Action Items")
        with st.form("quick_task"):
            new_t = st.text_input("Quick Add Task")
            if st.form_submit_button("Add to Inbox"):
                if new_t:
                    user_data["tasks"].append({"Task": new_t
