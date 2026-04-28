import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# 1. APP CONFIGURATION
st.set_page_config(page_title="Life OS", layout="centered", initial_sidebar_state="collapsed")

# 2. STATE MANAGEMENT (Simulating Database for Testing)
if "user_setup" not in st.session_state:
    st.session_state.user_setup = False
if "needs_review" not in st.session_state:
    st.session_state.needs_review = False
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "win_rate" not in st.session_state:
    st.session_state.win_rate = 0

# 3. PHASE 1: THE ONBOARDING QUESTIONNAIRE
if not st.session_state.user_setup:
    st.title("Welcome to your Life OS. 🚀")
    st.markdown("Let's build your perfect daily planner. Answer a few questions to set up your workflow.")
    
    with st.form("onboarding_form"):
        st.subheader("1. What is your primary focus this week?")
        focus = st.selectbox("Select Focus", ["Scaling Operations", "Business Development", "Personal Health & Routine", "All of the above"])
        
        st.subheader("2. Select your core daily habits:")
        habit_water = st.checkbox("Drink 1 Gallon of Water", value=True)
        habit_cardio = st.checkbox("Fasted Cardio")
        habit_reading = st.checkbox("Industry Reading (e.g., F1 Aero, Business Tech)")
        habit_bella = st.checkbox("Walk Bella")
        
        st.subheader("3. What are your non-negotiable tasks for today?")
        task1 = st.text_input("Task 1 (e.g., The Ohio Gym staff review, StretchLab marketing)")
        task2 = st.text_input("Task 2")
        
        submit_setup = st.form_submit_button("Build My Dashboard", type="primary", use_container_width=True)
        
        if submit_setup:
            # Build the dynamic task list based on answers
            if habit_water: st.session_state.tasks.append({"Task": "Drink 1 Gallon of Water", "Status": "Pending", "Urgent": False})
            if habit_cardio: st.session_state.tasks.append({"Task": "Fasted Cardio", "Status": "Pending", "Urgent": False})
            if habit_reading: st.session_state.tasks.append({"Task": "Industry Reading", "Status": "Pending", "Urgent": False})
            if habit_bella: st.session_state.tasks.append({"Task": "Walk Bella", "Status": "Pending", "Urgent": False})
            if task1: st.session_state.tasks.append({"Task": task1, "Status": "Pending", "Urgent": True})
            if task2: st.session_state.tasks.append({"Task": task2, "Status": "Pending", "Urgent": True})
            
            st.session_state.user_setup = True
            st.balloons()
            st.rerun()
    st.stop()

# 4. PHASE 2: FORCED WEEKLY REVIEW
if st.session_state.needs_review:
    st.title("🛑 Weekly Review Required")
    st.markdown("Before you attack the new week, you must review the tape.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Win Rate")
        completed = st.session_state.win_rate
        missed = 100 - completed if completed > 0 else 100
        fig = px.pie(
            values=[completed, missed], 
            names=["Crushed It", "Missed"],
            hole=0.7,
            color_discrete_sequence=["#00CC96", "#EF553B"]
        )
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Reflection Protocol")
        st.text_area("Wins: What went well this week?", placeholder="e.g., Booked 3 new intro sessions...")
        st.text_area("Adjustments: Where did we lose?", placeholder="e.g., Missed follow-ups on Thursday...")
        
        if st.button("Lock It In & Start New Week", type="primary", use_container_width=True):
            st.session_state.needs_review = False
            st.session_state.win_rate = 0 
            st.snow()
            st.rerun()
    st.stop()

# 5. PHASE 3: THE MAIN COMMAND CENTER
st.title("Command Center")
st.caption(f"{date.today().strftime('%A, %B %d, %Y')}")

colA, colB, colC = st.columns(3)
with colA:
    if st.button("➕ Add Quick Task"):
        st.session_state.tasks.append({"Task": "New Action Item", "Status": "Pending", "Urgent": False})
        st.rerun()
with colB:
    if st.button("🔄 Trigger Weekly Review"):
        st.session_state.win_rate = 85
        st.session_state.needs_review = True
        st.rerun()

st.divider()

st.subheader("Today's Playbook")
all_done = True
for idx, item in enumerate(st.session_state.tasks):
    if item["Status"] == "Pending":
        all_done = False
        icon = "❗" if item["Urgent"] else "◻️"
        
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"**{icon} {item['Task']}**")
        with c2:
            if st.button("Done", key=f"done_{idx}"):
                st.session_state.tasks[idx]["Status"] = "Completed"
                st.toast("Goal crushed! 🎯", icon="🔥")
                st.rerun()
    else:
        st.success(f"✅ ~{item['Task']}~")

# 6. PHASE 4: END OF DAY WRAP UP
st.divider()
with st.expander("🌙 End of Day Wrap-Up"):
    if all_done and len(st.session_state.tasks) > 0:
        st.success("You cleared the board today. Rest up.")
    else:
        pending_count = sum(1 for t in st.session_state.tasks if t["Status"] == "Pending")
        st.warning(f"You have {pending_count} pending tasks left.")
        colX, colY = st.columns(2)
        with colX:
            if st.button("Roll Over to Tomorrow"):
                st.toast("Tasks moved. Clock out.", icon="🌙")
        with colY:
            if st.button("Hustle & Finish Now", type="primary"):
                st.toast("Let's get it done.", icon="💪")
