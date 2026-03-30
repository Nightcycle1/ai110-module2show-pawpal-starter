class ScheduleEntry:
    def __init__(self, task: Task, start_time: int, end_time: int, reasoning: str):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reasoning = reasoning

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        """Initialize scheduler with owner and pet"""
        self.owner = owner
        self.pet = pet
        self.schedule = []
        self.unscheduled = []
        self.reasoning_log = []
    
    def load_tasks_from_pet(self) -> None:
        """Load all tasks from pet object"""
        pass
    
    def validate_time_feasibility(self) -> dict:
        """
        Check if total task time fits within available time
        Returns:
            dict with 'feasible' (bool), 'total_minutes', 'available_minutes', 'excess'
        """
        pass
    
    def schedule_fixed_time_tasks(self) -> list:
        """Schedule tasks that have fixed times"""
        pass
    
    def schedule_by_priority(self) -> list:
        """Schedule remaining tasks sorted by priority"""
        pass
    
    def find_time_slot(self, task: Task, scheduled_blocks: list) -> tuple:
        """
        Find earliest available time slot for a task
        Args:
            task: Task to schedule
            scheduled_blocks: List of (start, end) tuples of already scheduled tasks
        Returns:
            (start_time, end_time) tuple or None if no slot
        """
        pass
    
    def generate_plan(self) -> dict:
        """
        Main method to generate complete daily plan
        Returns:
            dict with:
                'scheduled': List of ScheduleEntry objects
                'unscheduled': List of tasks not scheduled
                'reasoning': List of explanation strings
                'feasibility': Dict with validation results
        """
        pass
    
    def explain_plan(self) -> list:
        """
        Generate human-readable explanations for the schedule
        Returns:
            List of explanation strings
        """
        pass
    
    def get_schedule_summary(self) -> dict:
        """
        Get summary statistics of the schedule
        Returns:
            dict with total_minutes_scheduled, num_tasks, etc.
        """
        pass