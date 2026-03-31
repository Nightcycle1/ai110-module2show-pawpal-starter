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
            end = current + duration_hours

            # Check if this slot overlaps with any already-scheduled block
            overlap = False
            for block_start, block_end in scheduled_blocks:
                # Overlap exists if the new task starts before a block ends
                # AND ends after a block starts
                if current < block_end and end > block_start:
                    overlap = True
                    # Jump to end of the conflicting block to avoid re-checking
                    current = block_end
                    break

            if not overlap:
                return (current, end)

            # If no jump happened inside the loop, advance by 30 min
            if current == owner_start or current < owner_start:
                current += 0.5
            # (current was already updated inside loop if overlap found)

        return None  # No slot found


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

        return {
            "total_minutes_scheduled": total_scheduled,
            "total_minutes_unscheduled": total_unscheduled,
            "num_tasks_scheduled": len(self.schedule),
            "num_tasks_unscheduled": len(self.unscheduled),
            "available_minutes": self.owner.get_available_minutes(),
            "minutes_remaining": self.owner.get_available_minutes() - total_scheduled
        }
