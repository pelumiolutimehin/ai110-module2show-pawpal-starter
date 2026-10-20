from datetime import date

import streamlit as st
from pawpal_system import Task, Priority, Scheduler, Owner, Pet

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
# Create the Owner once; later reruns get the same object (and its pets/tasks) back.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", 200)
owner: Owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=1, max_value=1440, value=owner.available_minutes)
)

st.caption(f"Planning for {owner.name} with {owner.available_minutes} minutes available today.")

st.subheader("Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    else:
        try:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as e:
            st.error(str(e))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    target_name = st.selectbox("Pet", [p.name for p in owner.pets])
    target_pet = next(p for p in owner.pets if p.name == target_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col1, col2 = st.columns(2)
    with col1:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col2:
        use_fixed_time = st.checkbox("Fixed time")
        fixed_time = st.time_input("Start time") if use_fixed_time else None

    if st.button("Add task"):
        target_pet.add_task(
            Task(task_title, int(duration), Priority[priority.upper()],
                 frequency=frequency, fixed_time=fixed_time)
        )
        st.success(f"Added '{task_title}' for {target_pet.name}.")
else:
    st.caption("Add a pet to start adding tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Pet": t.pet_name,
            "Task": t.title,
            "Minutes": t.duration,
            "Priority": t.priority.name.title(),
            "Frequency": t.frequency,
            "Fixed time": f"{t.fixed_time:%H:%M}" if t.fixed_time else "-",
            "Done": t.completed,
        }
        for t in all_tasks
    ])
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = Scheduler(owner).generate_plan(date.today())
    st.markdown(f"**Today's Schedule for {owner.name}** ({date.today():%A, %B %d}, "
                f"{owner.available_minutes} min available)")
    if plan.items:
        st.table([
            {
                "Time": f"{i.start_time:%H:%M} - {i.end_time:%H:%M}",
                "Pet": i.task.pet_name,
                "Task": i.task.title,
                "Priority": i.task.priority.name.title(),
                "Why": i.reason,
            }
            for i in plan.items
        ])
    else:
        st.info("Nothing to schedule today.")
    for s in plan.skipped:
        st.warning(f"Skipped '{s.task.title}' ({s.task.pet_name}): {s.reason}")
