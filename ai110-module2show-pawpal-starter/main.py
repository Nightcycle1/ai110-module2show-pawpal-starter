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
# Tasks are added OUT OF ORDER intentionally — low priority first, fixed last.
# This lets us verify the scheduler sorts and prioritizes correctly
# regardless of the order tasks were added to the pet.

# Optional low-priority task added first — should end up scheduled last
playtime = Task(
    title="Playtime",
    duration_minutes=45,
    priority="low",
    task_type="flexible",
    required=False
)

# Flexible high-priority task added second
feeding_dog = Task(
    title="Feeding (Mochi)",
    duration_minutes=15,
    priority="high",
    task_type="flexible",
    required=True
)

# Fixed task added last — must happen at 8am regardless of insertion order
morning_walk = Task(
    title="Morning Walk",
    duration_minutes=30,
    priority="high",
    task_type="fixed",
    fixed_time=8,
    required=True
)

# Added out of order: low -> high flexible -> high fixed
dog.add_task(playtime)
dog.add_task(feeding_dog)
dog.add_task(morning_walk)

print(f"\nMochi's tasks ({dog.get_task_count()} total, {dog.get_total_task_time()} min):")
for task in dog.get_tasks():
    print(f"  {task}")


# --- Create Tasks for Luna (cat) ---
# Also added out of order: optional grooming first, fixed medication last.

# Grooming is optional — added first but should be scheduled last
grooming = Task(
    title="Grooming",
    duration_minutes=20,
    priority="medium",
    task_type="flexible",
    required=False
)

# Feeding is required but flexible — added second
feeding_cat = Task(
    title="Feeding (Luna)",
    duration_minutes=10,
    priority="high",
    task_type="flexible",
    required=True
)

# Medication must happen at 9am — added last but should be anchored first
medication = Task(
    title="Medication (Luna)",
    duration_minutes=10,
    priority="high",
    task_type="fixed",
    fixed_time=9,
    required=True
)

# Added out of order: optional -> required flexible -> required fixed
cat.add_task(grooming)
cat.add_task(feeding_cat)
cat.add_task(medication)

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
print("FILTER + SORT DEMOS")
print("="*50)

# Re-run Mochi's scheduler so we have a live schedule to filter
dog_scheduler = Scheduler(owner=owner, pet=dog)
dog_scheduler.generate_plan()

# Mark the first scheduled task as complete so the filter has something to split on
if dog_scheduler.schedule:
    dog_scheduler.schedule[0].task.mark_complete()
    print(f"\nMarked '{dog_scheduler.schedule[0].task.title}' as complete.")

# Filter 1: incomplete tasks only — what still needs doing
incomplete = dog_scheduler.filter_schedule(completed=False)
print(f"\nMochi — incomplete tasks ({len(incomplete)} remaining):")
for entry in incomplete:
    print(f"  {entry}")

# Filter 2: completed tasks only — what's already done
done = dog_scheduler.filter_schedule(completed=True)
print(f"\nMochi — completed tasks ({len(done)} done):")
for entry in done:
    print(f"  {entry}")

# Filter 3: pet name match — should return all entries since pet is Mochi
matched = dog_scheduler.filter_schedule(pet_name="Mochi")
print(f"\nFilter by pet name 'Mochi' — {len(matched)} entries returned (expect all {len(dog_scheduler.schedule)}):")
for entry in matched:
    print(f"  {entry}")

# Filter 4: wrong pet name — should return empty list
no_match = dog_scheduler.filter_schedule(pet_name="Luna")
print(f"\nFilter by pet name 'Luna' on Mochi's scheduler — {len(no_match)} entries returned (expect 0)")

# Sort demo: show that schedule is sorted by start_time regardless of insertion order
print(f"\nMochi — full schedule sorted by start time (tasks were added low->high->fixed):")
for entry in sorted(dog_scheduler.schedule, key=lambda e: e.start_time):
    print(f"  {entry}")

print("\n" + "="*50)
print("CONFLICT DETECTION DEMO")
print("="*50)

# To trigger a conflict we give BOTH pets a fixed task at 8am.
# Each scheduler runs independently so neither knows about the other's
# fixed slot — detect_conflicts() is what catches the overlap afterward.

conflict_dog = Pet(name="Mochi", species="dog", age=3)
conflict_cat = Pet(name="Luna", species="cat", age=5)

# Both fixed at 8am, 30 minutes — guaranteed overlap
conflict_dog.add_task(Task(
    title="Morning Walk",
    duration_minutes=30,
    priority="high",
    task_type="fixed",
    fixed_time=8,
    required=True
))

conflict_cat.add_task(Task(
    title="Breakfast (Luna)",
    duration_minutes=20,
    priority="high",
    task_type="fixed",
    fixed_time=8,   # same slot as Morning Walk — intentional conflict
    required=True
))

# Also add a non-overlapping task so the schedule isn't trivially small
conflict_dog.add_task(Task(title="Feeding (Mochi)", duration_minutes=15, priority="medium"))
conflict_cat.add_task(Task(title="Grooming", duration_minutes=20, priority="low"))

# Run both schedulers independently
sched_dog = Scheduler(owner=owner, pet=conflict_dog)
sched_cat = Scheduler(owner=owner, pet=conflict_cat)
sched_dog.generate_plan()
sched_cat.generate_plan()

print("\nMochi's schedule:")
for entry in sched_dog.schedule:
    print(f"  {entry}")

print("\nLuna's schedule:")
for entry in sched_cat.schedule:
    print(f"  {entry}")

# Cross-pet conflict check — compares Mochi's entries against Luna's
print("\nRunning cross-pet conflict detection...")
conflicts = sched_dog.detect_conflicts(other_schedule=sched_cat.schedule)

if conflicts:
    print(f"\n  {len(conflicts)} conflict(s) found:")
    for warning in conflicts:
        print(f"  [!] {warning}")
else:
    print("  No conflicts detected.")

# Also verify same-pet self-check returns nothing (scheduler already prevents these)
self_conflicts = sched_dog.detect_conflicts()
print(f"\nSame-pet self-check for Mochi: {len(self_conflicts)} conflict(s) (expect 0)")

print("\n" + "="*50)
print("Done.")
