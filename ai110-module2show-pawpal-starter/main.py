"""
main.py - purpose is to test all other components to verify logic in the terminal.

- import classes
- create an owner and at least two pets
- Add at least 3 tasks with different times to those pets
- prints a "today's schedule" to the terminal
"""

# --- Imports ---
# Bring in all four classes so we can test them together end-to-end
from task import Task
from owner import Owner
from pet import Pet
from scheduler import Scheduler


# --- Create Owner ---
# Owner defines the available time window for the day.
# 8am-8pm gives us 720 minutes to work with.
owner = Owner(name="Jordan", available_hours_start=8, available_hours_end=20)
print(f"Owner created: {owner}")


# --- Create Pets ---
# Two pets so we can verify the scheduler handles tasks from different pets.
# Each pet gets its own Scheduler run since tasks are pet-specific.
dog = Pet(name="Mochi", species="dog", age=3)
cat = Pet(name="Luna", species="cat", age=5)
cat.set_notes("Needs medication with food — do not skip")

print(f"\nPets created:")
print(f"  {dog}")
print(f"  {cat}")


# --- Create Tasks for Mochi (dog) ---
# Mix of fixed, flexible, required, and optional to exercise all scheduler paths.

# Fixed task — must happen at 8am, no flexibility
morning_walk = Task(
    title="Morning Walk",
    duration_minutes=30,
    priority="high",
    task_type="fixed",
    fixed_time=8,
    required=True
)

# Flexible high-priority task — scheduler places this as early as possible
feeding_dog = Task(
    title="Feeding (Mochi)",
    duration_minutes=15,
    priority="high",
    task_type="flexible",
    required=True
)

# Optional low-priority task — gets scheduled only if time remains
playtime = Task(
    title="Playtime",
    duration_minutes=45,
    priority="low",
    task_type="flexible",
    required=False
)

dog.add_task(morning_walk)
dog.add_task(feeding_dog)
dog.add_task(playtime)

print(f"\nMochi's tasks ({dog.get_task_count()} total, {dog.get_total_task_time()} min):")
for task in dog.get_tasks():
    print(f"  {task}")


# --- Create Tasks for Luna (cat) ---
# Fixed medication time + flexible feeding + optional grooming

# Medication must happen at a specific time — fixed
medication = Task(
    title="Medication (Luna)",
    duration_minutes=10,
    priority="high",
    task_type="fixed",
    fixed_time=9,
    required=True
)

# Feeding is required but flexible — scheduler finds a slot
feeding_cat = Task(
    title="Feeding (Luna)",
    duration_minutes=10,
    priority="high",
    task_type="flexible",
    required=True
)

# Grooming is optional — nice to have but skippable
grooming = Task(
    title="Grooming",
    duration_minutes=20,
    priority="medium",
    task_type="flexible",
    required=False
)

cat.add_task(medication)
cat.add_task(feeding_cat)
cat.add_task(grooming)

print(f"\nLuna's tasks ({cat.get_task_count()} total, {cat.get_total_task_time()} min):")
for task in cat.get_tasks():
    print(f"  {task}")


# --- Run Scheduler for each pet ---
# Each pet gets its own Scheduler instance since tasks belong to one pet.
# The owner is shared — same time window applies to both.

print("\n" + "="*50)
print("GENERATING SCHEDULES")
print("="*50)

for pet in [dog, cat]:
    print(f"\n--- Today's Schedule for {pet.name} ---")

    scheduler = Scheduler(owner=owner, pet=pet)

    # Check feasibility before generating — warns if tasks exceed available time
    feasibility = scheduler.validate_time_feasibility()
    if not feasibility["feasible"]:
        print(f"  WARNING: Tasks exceed available time by {feasibility['excess']} minutes!")
    else:
        print(f"  Feasibility OK: {feasibility['total_minutes']} min of tasks, "
              f"{feasibility['available_minutes']} min available")

    # Generate the full plan
    plan = scheduler.generate_plan()

    # Print scheduled tasks in time order
    print(f"\n  Scheduled ({len(plan['scheduled'])} tasks):")
    for entry in plan["scheduled"]:
        print(f"    {entry}")

    # Print anything that couldn't fit
    if plan["unscheduled"]:
        print(f"\n  Could not schedule ({len(plan['unscheduled'])} tasks):")
        for task in plan["unscheduled"]:
            print(f"    - {task.title} ({task.duration_minutes} min)")

    # Print reasoning log — this is the "explain the plan" requirement
    print(f"\n  Reasoning:")
    for reason in plan["reasoning"]:
        print(f"    • {reason}")

    # Print summary stats
    summary = scheduler.get_schedule_summary()
    print(f"\n  Summary: {summary['num_tasks_scheduled']} tasks scheduled, "
          f"{summary['total_minutes_scheduled']} min used, "
          f"{summary['minutes_remaining']} min remaining")

print("\n" + "="*50)
print("Done.")
