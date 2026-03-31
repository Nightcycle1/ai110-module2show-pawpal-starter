from owner import Owner
from pet import Pet
from task import Task


class ScheduleEntry:
    """
    Represents a single scheduled task with its time slot and reasoning.
    This is what the scheduler outputs — one entry per scheduled task.
    """
    def __init__(self, task: Task, start_time: int, end_time: int, reasoning: str):
        self.task = task
        self.start_time = start_time    # Hour (0-23) when task starts
        self.end_time = end_time        # Hour (decimal) when task ends e.g. 8.5 = 8:30
        self.reasoning = reasoning      # Human-readable explanation of why/when

    def __str__(self) -> str:
        """Format entry for display in UI"""
        # Convert decimal hours to HH:MM format e.g. 8.5 -> "08:30"
        start_h = int(self.start_time)
        start_m = int((self.start_time % 1) * 60)
        end_h = int(self.end_time)
        end_m = int((self.end_time % 1) * 60)
        return (f"{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d} | "
                f"{self.task.title} ({self.task.duration_minutes} min) | "
                f"{self.task.priority_str.upper()}")


class Scheduler:
    """
    Core scheduling logic for PawPal+.

    Scheduling order:
      1. Fixed-time tasks (must happen at a specific hour)
      2. Required flexible tasks (sorted by priority, then duration)
      3. Optional flexible tasks (sorted by priority, then duration)

    If tasks don't fit in available time, they go into self.unscheduled.
    """

    def __init__(self, owner: Owner, pet: Pet):
        """
        Initialize scheduler with owner and pet.
        Both are needed because:
          - Owner provides the available time window
          - Pet provides the list of tasks and any notes/constraints
        """
        self.owner = owner
        self.pet = pet
        self.schedule: list[ScheduleEntry] = []    # Final ordered schedule
        self.unscheduled: list[Task] = []          # Tasks that didn't fit
        self.reasoning_log: list[str] = []         # All reasoning messages


    def load_tasks_from_pet(self) -> list[Task]:
        """
        Pull tasks from the pet object.
        Returns the raw list so generate_plan() can work with it.
        """
        return self.pet.get_tasks()


    def validate_time_feasibility(self) -> dict:
        """
        Check if the total task time fits within the owner's available window.
        This is a quick sanity check before scheduling — if total task time
        exceeds available time, some tasks will definitely be unscheduled.

        Returns a dict so the UI can display useful feedback to the user.
        """
        total_minutes = self.pet.get_total_task_time()
        available_minutes = self.owner.get_available_minutes()
        excess = total_minutes - available_minutes

        return {
            "feasible": total_minutes <= available_minutes,
            "total_minutes": total_minutes,
            "available_minutes": available_minutes,
            "excess": max(0, excess)  # Only positive if over limit
        }


    def find_time_slot(self, task: Task, scheduled_blocks: list[tuple]) -> tuple | None:
        """
        Find the earliest available time slot for a task.

        @param task - Task to place
        @param scheduled_blocks - List of (start, end) tuples already occupied

        How it works:
          - Start at the owner's available start hour
          - Try each 30-minute increment as a potential start time
          - Check if the task fits (no overlap with existing blocks, within owner window)
          - Return the first slot that works, or None if no slot found

        30-minute granularity is a reasonable balance — fine enough for real
        scheduling but not so granular it's slow to compute.
        """
        owner_start = self.owner.available_hours_start
        owner_end = self.owner.available_hours_end
        duration_hours = task.duration_minutes / 60.0

        # Try every 30-minute increment within the owner's window
        current = owner_start
        
        while current + duration_hours <= owner_end:
            # Calculate where this task would end if it started right now
            end = current + duration_hours
            # Assume no conflict until proven otherwise
            jumped = False

            # Check the candidate slot against every already-scheduled block
            for block_start, block_end in scheduled_blocks:
                # Overlap condition: new task starts before a block ends AND ends after a block starts
                # (standard interval overlap check)
                if current < block_end and end > block_start:
                    # Conflict found — jump past the conflicting block entirely
                    # so we don't waste iterations checking times we know are taken
                    current = block_end
                    jumped = True
                    break  # Re-check all blocks from the new position

            if not jumped:
                # No conflict found with any existing block — this slot is free
                return (current, end)

        # Reached the end of the owner's available window with no valid slot
        return None



    def schedule_fixed_time_tasks(self, scheduled_blocks: list[tuple]) -> list[ScheduleEntry]:
        """
        Schedule tasks that must happen at a specific hour first.
        Fixed tasks have no flexibility — they go at their fixed_time or not at all.

        Modifies scheduled_blocks in place so subsequent methods know these slots are taken.
        """
        entries = []
        fixed_tasks = self.pet.get_fixed_time_tasks()

        for task in fixed_tasks:
            start = task.fixed_time
            end = start + (task.duration_minutes / 60.0)

            # Check the fixed slot isn't already occupied
            overlap = any(start < b_end and end > b_start
                          for b_start, b_end in scheduled_blocks)

            if overlap:
                # Can't move a fixed task — it simply can't be scheduled
                self.unscheduled.append(task)
                reason = (f"'{task.title}' could not be scheduled at {start}:00 "
                          f"due to a conflict with another fixed task.")
                self.reasoning_log.append(reason)
            else:
                scheduled_blocks.append((start, end))
                reason = task.get_scheduling_reasoning(start)
                self.reasoning_log.append(reason)
                entries.append(ScheduleEntry(task, start, end, reason))

        return entries


    def schedule_by_priority(self, tasks: list[Task], scheduled_blocks: list[tuple]) -> list[ScheduleEntry]:
        """
        Schedule a list of flexible tasks sorted by priority.

        Sorting logic:
          - Primary: priority_value descending (high=5 before medium=3 before low=1)
          - Secondary: duration_minutes descending (longer required tasks placed first
            when priority is tied — gets the hard placements done early)
          - Tertiary: required before optional (extra safety net for ties)

        Each task gets the earliest available slot via find_time_slot().
        If no slot exists, it goes to unscheduled.
        """
        entries = []

        # Sort: highest priority first, then longest duration, then required first
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.priority_value, t.duration_minutes, t.required),
            reverse=True
        )

        for task in sorted_tasks:
            slot = self.find_time_slot(task, scheduled_blocks)

            if slot is None:
                # No room left — task can't be scheduled today
                self.unscheduled.append(task)
                reason = (f"'{task.title}' could not be scheduled — "
                          f"not enough time remaining in the day.")
                self.reasoning_log.append(reason)
            else:
                start, end = slot
                scheduled_blocks.append((start, end))  # Mark slot as taken
                reason = task.get_scheduling_reasoning(start)
                self.reasoning_log.append(reason)
                entries.append(ScheduleEntry(task, start, end, reason))

        return entries


    def generate_plan(self) -> dict:
        """
        Main entry point — builds the complete daily schedule.

        Steps:
          1. Validate feasibility (warn user if tasks exceed available time)
          2. Schedule fixed-time tasks first (they have no flexibility)
          3. Schedule required flexible tasks next (mandatory, sorted by priority)
          4. Schedule optional flexible tasks last (nice-to-have)
          5. Sort the final schedule chronologically by start time
          6. Return everything the UI needs to display the plan

        Returns a dict so app.py can unpack exactly what it needs.
        """
        # Reset state in case generate_plan() is called more than once
        self.schedule = []
        self.unscheduled = []
        self.reasoning_log = []

        # Track occupied time blocks as (start, end) tuples
        scheduled_blocks: list[tuple] = []

        # Step 1 — feasibility check
        feasibility = self.validate_time_feasibility()
        if not feasibility["feasible"]:
            self.reasoning_log.append(
                f"Warning: Total task time ({feasibility['total_minutes']} min) exceeds "
                f"available time ({feasibility['available_minutes']} min) by "
                f"{feasibility['excess']} minutes. Some tasks will be unscheduled."
            )

        # Step 2 — fixed-time tasks
        fixed_entries = self.schedule_fixed_time_tasks(scheduled_blocks)
        self.schedule.extend(fixed_entries)

        # Step 3 — required flexible tasks
        required_flexible = [t for t in self.pet.get_required_tasks() if not t.is_fixed()]
        required_entries = self.schedule_by_priority(required_flexible, scheduled_blocks)
        self.schedule.extend(required_entries)

        # Step 4 — optional flexible tasks
        optional_flexible = [t for t in self.pet.get_optional_tasks() if not t.is_fixed()]
        optional_entries = self.schedule_by_priority(optional_flexible, scheduled_blocks)
        self.schedule.extend(optional_entries)

        # Step 5 — sort chronologically so the UI can display in time order
        self.schedule.sort(key=lambda entry: entry.start_time)

        return {
            "scheduled": self.schedule,
            "unscheduled": self.unscheduled,
            "reasoning": self.reasoning_log,
            "feasibility": feasibility
        }


    def mark_task_complete(self, task: Task) -> Task | None:
        """
        Mark a task as complete and automatically queue the next occurrence
        if the task is recurring (frequency="daily" or "weekly").

        @param task - The Task object to mark as done (must belong to this pet)

        @return - The new Task instance added to the pet if recurring, else None.

        How it works:
          - Always calls task.mark_complete() to set completed=True
          - If the task has a frequency, calls task.next_occurrence() to create
            a fresh copy, then adds it to the pet so it appears in the next
            call to generate_plan()
          - One-off tasks (frequency=None) are simply marked done — nothing is queued
        """
        task.mark_complete()

        if task.frequency is not None:
            # Create a fresh uncompleted copy for the next cycle
            next_task = task.next_occurrence()
            self.pet.add_task(next_task)
            self.reasoning_log.append(
                f"'{task.title}' completed ({task.frequency} task) — "
                f"next occurrence queued automatically."
            )
            return next_task

        return None  # One-off task — nothing queued


    def detect_conflicts(self, other_schedule: list = None) -> list[str]:
        """
        Lightweight conflict detection — returns warning strings instead of raising.

        Checks two scenarios:
          1. Within this scheduler's own schedule (same-pet self-overlap)
          2. Against another scheduler's schedule (cross-pet overlap), if provided

        @param other_schedule - Optional list of ScheduleEntry from a second Scheduler
                                (e.g. a second pet's schedule sharing the same owner).
                                Pass None to only check within this schedule.

        @return - List of human-readable warning strings, one per conflict found.
                  Empty list means no conflicts detected.

        Strategy — pairwise interval overlap check:
          For each pair of entries (A, B), a conflict exists when:
              A.start_time < B.end_time  AND  A.end_time > B.start_time
          This is the standard interval overlap condition. It's O(n²) but
          lightweight for the small task counts typical in a daily pet schedule.
        """
        warnings = []

        # Combine this schedule with the other (if provided) into one flat list,
        # tagging each entry with a label so the warning message is readable
        tagged = [(entry, self.pet.name) for entry in self.schedule]
        if other_schedule:
            # Infer the other pet's name from the first entry if possible
            other_label = "Other pet"
            if other_schedule and hasattr(other_schedule[0].task, "title"):
                other_label = "Other pet"  # caller can pass pet name separately if needed
            tagged += [(entry, other_label) for entry in other_schedule]

        # Pairwise check — compare every entry against every later entry
        for i in range(len(tagged)):
            for j in range(i + 1, len(tagged)):
                entry_a, label_a = tagged[i]
                entry_b, label_b = tagged[j]

                # Standard interval overlap: A starts before B ends AND A ends after B starts
                if entry_a.start_time < entry_b.end_time and entry_a.end_time > entry_b.start_time:
                    warnings.append(
                        f"CONFLICT: '{entry_a.task.title}' ({label_a}, "
                        f"{entry_a.start_time:.2f}-{entry_a.end_time:.2f}) overlaps with "
                        f"'{entry_b.task.title}' ({label_b}, "
                        f"{entry_b.start_time:.2f}-{entry_b.end_time:.2f})"
                    )

        return warnings


    def filter_schedule(self, completed: bool = None, pet_name: str = None) -> list:
        """
        Filter the current schedule by completion status and/or pet name.

        @param completed  - If True, return only completed tasks.
                            If False, return only incomplete tasks.
                            If None, completion status is not filtered.
        @param pet_name   - If provided, only return entries whose pet matches
                            this name (case-insensitive). Useful when extending
                            to multi-pet schedules.

        @return - Filtered list of ScheduleEntry objects matching all given criteria.

        Example usage:
            # All incomplete tasks for a specific pet
            remaining = scheduler.filter_schedule(completed=False, pet_name="Mochi")
        """
        results = self.schedule

        # Filter by completion status using a lambda on the task's completed flag
        if completed is not None:
            results = list(filter(lambda entry: entry.task.completed == completed, results))

        # Filter by pet name — all entries belong to the same pet in this scheduler,
        # so if the name doesn't match, no entries qualify
        if pet_name is not None:
            if self.pet.name.lower() != pet_name.lower():
                results = []

        return results


    def explain_plan(self) -> list[str]:
        """
        Return the reasoning log — one string per scheduling decision.
        Called by the UI to display the 'why' behind the schedule.
        """
        return self.reasoning_log


    def get_schedule_summary(self) -> dict:
        """
        Compute summary statistics for display at the top of the results section.
        Gives the user a quick overview before they read the full schedule.
        """
        total_scheduled = sum(e.task.duration_minutes for e in self.schedule)
        total_unscheduled = sum(t.duration_minutes for t in self.unscheduled)
        
        # Was called twice
        available = self.owner.get_available_minutes()
        
        return {
            "total_minutes_scheduled": total_scheduled,
            "total_minutes_unscheduled": total_unscheduled,
            "num_tasks_scheduled": len(self.schedule),
            "num_tasks_unscheduled": len(self.unscheduled),
            "available_minutes": available,
            "minutes_remaining": available - total_scheduled
        }
