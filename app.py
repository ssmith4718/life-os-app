import streamlit as st
from datetime import datetime, date, time, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Life OS Premium", layout="wide")

# --- 1. LOCAL MEMORY ---
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def init_user_data(username, wake_time):
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            "wake_up": wake_time,
            "events": [],
            "tasks": [],
            "goals": []
        }

# --- 2. LOGIN & PROFILE GATEWAY ---
if st.session_state.current_user is None:
    st.title("Life OS")
    st.markdown("Create your profile to build your dashboard.")
    
    with st.container(border=True):
        st.subheader("New User Setup")
        with st.form("register_form"):
            new_user = st.text_input("Username")
            wake_time = st.time_input("What time do you wake up every day?", value=time(5, 30))
            if st.form_submit_button("Launch My Dashboard", type="primary"):
                if new_user:
                    init_user_data(new_user, wake_time)
                    st.session_state.current_user = new_user
                    st.rerun()
                    
    with st.container(border=True):
        st.subheader("Existing Login")
        with st.form("login_form"):
            existing_user = st.text_input("Username")
            if st.form_submit_button("Log In"):
                if existing_user in st.session_state.users:
                    st.session_state.current_user = existing_user
                    st.rerun()
                else:
                    st.error("User not found.")
    st.stop()

# --- 3. MAIN DASHBOARD ---
user = st.session_state.current_user
user_data = st.session_state.users[user]

st.sidebar.title(f"👤 {user}")
st.sidebar.caption(f"Wake Time: {user_data['wake_up'].strftime('%I:%M %p')}")
if st.sidebar.button("Log Out"):
    st.session_state.current_user = None
    st.rerun()

# Auto-generate the wake-up blocks for the current week
today = date.today()
start_of_week = today - timedelta(days=today.weekday())
for i in range(7):
    day = start_of_week + timedelta(days=i)
    wake_datetime = datetime.combine(day, user_data['wake_up'])
    end_datetime = wake_datetime + timedelta(minutes=15)
    
    # Ensure we don't duplicate wake-up blocks
    if not any(e['title'] == "🌅 Wake Up & Hydrate" and e['start'] == wake_datetime.isoformat() for e in user_data['events']):
        user_data['events'].append({
            "title": "🌅 Wake Up & Hydrate",
            "start": wake_datetime.isoformat(),
            "end": end_datetime.isoformat(),
            "backgroundColor": "#FFD700",
            "borderColor": "#FFD700"
        })

st.title("Command Center")

# --- SPLIT LAYOUT (SaaS DASHBOARD STYLE) ---
# Left column for Tasks/Goals, Right column for Calendar
col_left, col_right = st.columns([1, 2.5])

with col_left:
    # TASK WIDGET
    with st.container(border=True):
        st.subheader("✅ Action Items")
        with st.form("quick_task"):
            new_t = st.text_input("Quick Add Task", placeholder="e.g., Finalize Q3 Report")
            if st.form_submit_button("Add to Inbox"):
                if new_t:
                    user_data["tasks"].append({"Task": new_t, "Done": False})
                    st.rerun()
        
        # Display tasks with interaction
        if not user_data["tasks"]:
            st.caption("Inbox zero.")
        for idx, t in enumerate(user_data["tasks"]):
            if not t["Done"]:
                st.markdown(f"**{t['Task']}**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Complete", key=f"done_{idx}", use_container_width=True):
                        user_data["tasks"][idx]["Done"] = True
                        st.rerun()
                with c2:
                    # The interaction: Schedule a raw task onto the calendar
                    with st.popover("📅 Schedule"):
                        sched_date = st.date_input("Date", today, key=f"d_{idx}")
                        sched_time = st.time_input("Time", value=time(12, 0), step=300, key=f"t_{idx}")
                        if st.button("Push to Calendar", key=f"push_{idx}", type="primary"):
                            start_dt = datetime.combine(sched_date, sched_time)
                            end_dt = start_dt + timedelta(minutes=30)
                            user_data["events"].append({
                                "title": t['Task'],
                                "start": start_dt.isoformat(),
                                "end": end_dt.isoformat(),
                                "backgroundColor": "#FF4B4B",
                                "borderColor": "#FF4B4B"
                            })
                            # Mark as done in the inbox so it moves purely to the calendar
                            user_data["tasks"][idx]["Done"] = True 
                            st.rerun()
                st.divider()

    # GOALS WIDGET
    with st.container(border=True):
        st.subheader("🎯 Active Goals")
        with st.popover("➕ New Goal"):
            g_name = st.text_input("Goal Name")
            g_target = st.number_input("Target Number", min_value=1, value=10)
            if st.button("Save Goal", type="primary"):
                user_data["goals"].append({"Goal": g_name, "Current": 0, "Target": g_target})
                st.rerun()
                
        for idx, g in enumerate(user_data["goals"]):
            st.caption(f"{g['Goal']} ({g['Current']}/{g['Target']})")
            st.progress(min(g["Current"] / g["Target"], 1.0))
            if st.button("Log Progress (+1)", key=f"g_prog_{idx}"):
                user_data["goals"][idx]["Current"] += 1
                st.rerun()

with col_right:
    # MASTER CALENDAR WIDGET
    with st.container(border=True):
        # Dynamically set the scroll time to the user's wake-up time!
        wake_str = user_data["wake_up"].strftime("%H:%M:%S")
        
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "timeGridDay,timeGridWeek,dayGridMonth",
            },
            "initialView": "timeGridWeek",
            "slotDuration": "00:05:00",
            "snapDuration": "00:05:00",
            "scrollTime": wake_str, # Auto-scrolls to their wake up time
            "height": "850px",
            "nowIndicator": True, # Shows the red line for current time
        }
        calendar(events=user_data["events"], options=calendar_options)
