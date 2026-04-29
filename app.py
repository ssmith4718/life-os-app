import streamlit as st
from datetime import datetime, date, time, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Life OS Premium", layout="wide")

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
            "wake_up": time(5, 30), # Default, updated in setup
            "events": [],
            "tasks": [],
            "goals": []
        }

# --- 2. AUTHENTICATION GATEWAY ---
if st.session_state.current_user is None:
    st.title("Life OS")
    st.markdown("Log in or create an account to access your command center.")
    
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

# --- 4. THE ONBOARDING QUESTIONNAIRE ---
if not user_data["setup_complete"]:
    st.title("Let's build your operating system. 🚀")
    st.markdown("Answer a few questions so we can prepopulate your calendar and queue up your macro goals.")
    
    with st.form("setup_questionnaire"):
        st.subheader("1. Daily Anchors")
        wake_time = st.time_input("What time do you wake up?", value=time(5, 0))
        
        st.subheader("2. Professional Targets (Queues Goals)")
        biz_goals = st.multiselect("Select your core business objectives:", [
            "StretchLab Avon: Hit 200+ Members",
            "Gym Management: Staff & Protocol Updates",
            "Tech: Build AI API Integrations",
            "Sales: 50 Weekly Cold Outreaches"
        ])
        
        st.subheader("3. Personal & Fitness Routines (Pre-loads Calendar)")
        routines = st.multiselect("Select daily routines to auto-schedule:", [
            "Fasted Cardio (Morning)",
            "Heavy Lifting / Bodybuilding Split",
            "Walk Bella",
            "Plant Care / Propagation check",
            "Read Tech/F1 Regulations"
        ])
        
        if st.form_submit_button("Generate My Dashboard", type="primary", use_container_width=True):
            user_data["wake_up"] = wake_time
            
            # Auto-queue the selected goals
            for goal in biz_goals:
                # Assign default targets based on the goal type
                target_num = 200 if "200+" in goal else 50 if "50" in goal else 10
                user_data["goals"].append({"Goal": goal, "Current": 0, "Target": target_num})
            
            # Auto-populate the calendar for the current week based on routines
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            
            for i in range(7):
                day = start_of_week + timedelta(days=i)
                
                # Always add Wake Up
                wake_dt = datetime.combine(day, wake_time)
                user_data["events"].append({
                    "title": "🌅 Wake Up", "start": wake_dt.isoformat(), 
                    "end": (wake_dt + timedelta(minutes=15)).isoformat(), "backgroundColor": "#FFD700"
                })
                
                # Add conditional routines
                if "Fasted Cardio (Morning)" in routines:
                    cardio_dt = wake_dt + timedelta(minutes=30)
                    user_data["events"].append({
                        "title": "🏃 Fasted Cardio", "start": cardio_dt.isoformat(), 
                        "end": (cardio_dt + timedelta(minutes=45)).isoformat(), "backgroundColor": "#00CC96"
                    })
                if "Walk Bella" in routines:
                    walk_dt = datetime.combine(day, time(17, 30)) # 5:30 PM default
                    user_data["events"].append({
                        "title": "🐕 Walk Bella", "start": walk_dt.isoformat(), 
                        "end": (walk_dt + timedelta(minutes=30)).isoformat(), "backgroundColor": "#FF9F36"
                    })
                if "Heavy Lifting / Bodybuilding Split" in routines:
                    lift_dt = datetime.combine(day, time(18, 0)) # 6:00 PM default
                    user_data["events"].append({
                        "title": "🏋️ Bodybuilding Split", "start": lift_dt.isoformat(), 
                        "end": (lift_dt + timedelta(hours=1, minutes=30)).isoformat(), "backgroundColor": "#FF4B4B"
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
                    user_data["tasks"].append({"Task": new_t, "Done": False})
                    st.rerun()
        
        if not user_data["tasks"]: st.caption("Inbox zero.")
        for idx, t in enumerate(user_data["tasks"]):
            if not t["Done"]:
                st.markdown(f"**{t['Task']}**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Complete", key=f"done_{idx}", use_container_width=True):
                        user_data["tasks"][idx]["Done"] = True
                        st.rerun()
                with c2:
                    with st.popover("📅 Schedule"):
                        sched_date = st.date_input("Date", date.today(), key=f"d_{idx}")
                        sched_time = st.time_input("Time", value=time(12, 0), step=300, key=f"t_{idx}")
                        if st.button("Push to Calendar", key=f"push_{idx}", type="primary"):
                            start_dt = datetime.combine(sched
