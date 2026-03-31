import streamlit as st

# --- Imports ---
# Bring in all four classes
from task import Task
from owner import Owner
from pet import Pet
from scheduler import Scheduler

def format_time(hour_decimal):
    """Convert decimal hour to HH:MM format"""
    hour = int(hour_decimal)
    minute = int((hour_decimal % 1) * 60)
    return f"{hour:02d}:{minute:02d}"

# Tab information
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session states
if "owner" not in st.session_state:
    st.session_state.owner = Owner()

if "pet" not in st.session_state:
    st.session_state.pet = Pet()

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Title
st.title("🐾 PawPal+")

# Welcome message 
st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

# Scenario Expandable Info Box
with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

# Build Requirements Expandbale Info Box 
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




# Divider line
st.divider()


# Demo Inputs: Owner Name, Pet Name, species selection box
st.subheader("Quick Demo Inputs (UI only)")


col1, col2, col3 = st.columns(3)

with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    if owner_name:
        st.session_state.owner.set_name(owner_name)


with col2:
    # ADDED: Owner available hours
    avail_start = st.number_input("Available from (hour)", min_value=0, max_value=23, value=8)
    avail_end = st.number_input("Available until (hour)", min_value=1, max_value=24, value=20)
    if (avail_start, avail_end) != (st.session_state.owner.available_hours_start, 
                                     st.session_state.owner.available_hours_end):
        try:
            st.session_state.owner.set_available_hours(avail_start, avail_end)
        except ValueError as e:
            st.error(f"Invalid hours: {e}")



# Initialize session states for pet_name and species if they exist
with col3:
    pet_name = st.text_input("Pet name", value="Mochi")
    if pet_name:
        st.session_state.pet.set_name(pet_name)
    
    species = st.selectbox("Species", Pet.VALID_SPECIES)
    if species:
        st.session_state.pet.set_species(species)
    
    # ADDED: Pet age
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    if age != st.session_state.pet.age:
        st.session_state.pet.set_age(age)


# ADDED: Special notes section (new row)
notes = st.text_area("Special needs / notes (optional)", value=st.session_state.pet.notes)
if notes != st.session_state.pet.notes:
    st.session_state.pet.set_notes(notes)

# Divider line
st.divider()

# Tasks section
st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")


    


col1, col2, col3, col4 = st.columns(4)

with col1:
    task_title = st.text_input("Task title", value="Morning walk")

with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

with col4:
    # ADDED: Task type selection
    task_type = st.selectbox("Task type", ["flexible", "fixed"], index=0)


# ADDED: Conditional fixed time input (new row)
fixed_time = None
if task_type == "fixed":
    fixed_time = st.number_input("Fixed time (hour)", min_value=0, max_value=23, value=8)

# ADDED: Required and recurrence options (new row)
col5, col6 = st.columns(2)
with col5:
    required = st.checkbox("Required (cannot be skipped)", value=False)
with col6:
    frequency = st.selectbox("Recurrence", ["None", "daily", "weekly"], index=0)
    frequency = None if frequency == "None" else frequency


# In the add task section, add explicit instance creation:
if st.button("Add task"):
    if not task_title:
        st.error("Please enter a task title")
    else:
        try:
            # Create task instance
            new_task_instance = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                task_type=task_type,
                fixed_time=fixed_time,
                required=required,
                frequency=frequency
            )
            
            # Verify it's an instance
            print(f"Task type: {type(new_task_instance)}")  # Should be <class 'task.Task'>
            print(f"Is instance: {isinstance(new_task_instance, Task)}")  # Should be True
            
            st.session_state.pet.add_task(new_task_instance)
            st.success(f"Added: {task_title}")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            import traceback
            st.code(traceback.format_exc())


# Display current tasks
if st.session_state.pet.get_task_count() > 0:
    st.write("Current tasks:")
    
    # MODIFIED: Enhanced task display with all attributes
    task_data = []
    for task in st.session_state.pet.get_tasks():
        task_data.append({
            "Title": task.title,
            "Duration": f"{task.duration_minutes} min",
            "Priority": task.priority_str.upper(),
            "Type": task.task_type,
            "Fixed Time": f"{task.fixed_time}:00" if task.is_fixed() else "-",
            "Required": "Yes" if task.required else "No",
            "Recurrence": task.frequency if task.frequency else "-"
        })
    st.table(task_data)
    
    # ADDED: Delete functionality
    st.write("Remove tasks:")
    task_names = [task.title for task in st.session_state.pet.get_tasks()]
    task_to_delete = st.selectbox("Select task to remove", ["None"] + task_names)
    if task_to_delete != "None" and st.button("Remove selected task"):
        if st.session_state.pet.remove_task_by_title(task_to_delete):
            st.success(f"Removed: {task_to_delete}")
            st.rerun()
        else:
            st.error("Task not found")
    
else:
    st.info("No tasks yet. Add one above.")



# Divider
st.divider()

# Add a conflict check button before generating schedule
st.subheader("🔍 Check for Conflicts")
if st.button("Check for conflicts"):
    fixed_tasks = st.session_state.pet.get_fixed_time_tasks()
    fixed_times = {}
    
    # Group tasks by fixed time
    for task in fixed_tasks:
        if task.fixed_time not in fixed_times:
            fixed_times[task.fixed_time] = []
        fixed_times[task.fixed_time].append(task)
    
    # Display conflicts
    conflicts_found = False
    for time, tasks in fixed_times.items():
        if len(tasks) > 1:
            conflicts_found = True
            st.error(f"⚠️ Conflict at {time}:00")
            for task in tasks:
                st.markdown(f"   - {task.title} (priority: {task.priority_str})")
    
    if not conflicts_found:
        st.success("✅ No conflicts detected in fixed-time tasks")
    
    # Check total time
    total_minutes = st.session_state.pet.get_total_task_time()
    available_minutes = st.session_state.owner.get_available_minutes()
    
    if total_minutes > available_minutes:
        st.warning(f"⚠️ Total task time ({total_minutes} min) exceeds available time ({available_minutes} min) by {total_minutes - available_minutes} min")

# Build Schedule Section
st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if st.session_state.pet.get_task_count() == 0:
        st.warning("No tasks added yet. Add at least one task above.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=st.session_state.pet
        )
        plan = scheduler.generate_plan()

        # ===== ENHANCED CONFLICT WARNINGS =====
        # Check for fixed-time conflicts within this pet
        fixed_tasks = st.session_state.pet.get_fixed_time_tasks()
        fixed_times = [task.fixed_time for task in fixed_tasks]
        duplicate_times = [time for time in set(fixed_times) if fixed_times.count(time) > 1]
        
        if duplicate_times:
            st.error("⚠️ **CONFLICT DETECTED**")
            st.markdown(f"Multiple tasks scheduled at the same time: **{', '.join(str(t) + ':00' for t in duplicate_times)}**")
            st.markdown("Only the highest priority task at each time will be scheduled.")
        
        # Feasibility warning
        if not plan["feasibility"]["feasible"]:
            st.warning(
                f"⚠️ Total task time ({plan['feasibility']['total_minutes']} min) exceeds "
                f"available time ({plan['feasibility']['available_minutes']} min) by "
                f"{plan['feasibility']['excess']} min. Some tasks were skipped."
            )
        
        # Check for cross-pet conflicts (if you have multiple pets)
        # This would need to be expanded if you support multiple pets

        # Display scheduled tasks with visual indicators
        st.subheader("📅 Today's Schedule")
        if plan["scheduled"]:
            for entry in plan["scheduled"]:
                # Color code by priority
                priority_color = {
                    "high": "🔴",
                    "medium": "🟡", 
                    "low": "🟢"
                }.get(entry.task.priority_str, "⚪")
                
                # Show required badge
                required_badge = "⭐ **REQUIRED** " if entry.task.required else ""
                
                # Format times using the helper function
                start_str = format_time(entry.start_time)
                end_str = format_time(entry.end_time)
                
                st.markdown(
                    f"{priority_color} **{start_str} - {end_str}** | "
                    f"{entry.task.title} ({entry.task.duration_minutes} min) {required_badge}"
                )
                
                # Show reasoning in smaller text
                st.caption(f"💡 {entry.reasoning}")
                st.divider()
        else:
            st.info("No tasks could be scheduled.")
            
        # Display unscheduled tasks with conflict explanations
        if plan["unscheduled"]:
            st.subheader("❌ Could Not Schedule")
            for task in plan["unscheduled"]:
                # Check if this task conflicted with something
                conflict_reason = "Time conflict with higher priority task"
                if task.is_fixed():
                    conflict_reason = f"Fixed time {task.fixed_time}:00 already occupied"
                elif plan["feasibility"]["excess"] > 0:
                    conflict_reason = "Not enough time in schedule"
                    
                st.markdown(
                    f"• **{task.title}** ({task.duration_minutes} min, priority: {task.priority_str}) "
                    f"- *{conflict_reason}*"
                )
        
        # Display reasoning in an expander
        with st.expander("📋 View detailed reasoning"):
            for i, reason in enumerate(plan["reasoning"], 1):
                st.markdown(f"{i}. {reason}")

        # Summary stats with visual indicators
        summary = scheduler.get_schedule_summary()
        
        # Color code the summary based on remaining time
        remaining_minutes = summary['minutes_remaining']
        if remaining_minutes < 0:
            status_color = "🔴"
        elif remaining_minutes < 60:
            status_color = "🟡"
        else:
            status_color = "🟢"
            
        st.info(
            f"{status_color} **Schedule Summary**  \n"
            f"📋 {summary['num_tasks_scheduled']} tasks scheduled  \n"
            f"⏱️ {summary['total_minutes_scheduled']} min used  \n"
            f"✨ {summary['minutes_remaining']} min remaining  \n"
            f"⏰ Available: {summary['available_minutes']} min total"
        )

    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
