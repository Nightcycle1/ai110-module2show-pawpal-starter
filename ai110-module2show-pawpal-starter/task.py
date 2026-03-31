class Task:
    # Priority mapping for UI (low, medium, high) to numeric values
    PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}
    REVERSE_PRIORITY_MAP = {1: "low", 3: "medium", 5: "high"} # To convert numeric back to string
    
    VALID_FREQUENCIES = {None, "daily", "weekly"}

    def __init__(self, title: str = "", duration_minutes: int = 20,
                 priority: str = "medium", task_type: str = "flexible",
                 fixed_time: int = None, required: bool = False,
                 frequency: str = None):
        """
        Initialize task with attributes matching UI inputs
        Args:
            title: Task name (from UI)
            duration_minutes: Duration in minutes (from UI)
            priority: "low", "medium", or "high" (from UI)
            task_type: "flexible" or "fixed"
            fixed_time: Hour (0-23) if fixed
            required: Whether task is mandatory
            frequency: Recurrence — None (one-off), "daily", or "weekly"
        """
        self.title = title
        self.duration_minutes = duration_minutes
        if priority not in self.PRIORITY_MAP:
            raise ValueError(f"Invalid priority: '{priority}'. Must be one of {list(self.PRIORITY_MAP.keys())}")
        self.priority_str = priority
        self.priority_value = self.PRIORITY_MAP[priority]
        self.task_type = task_type
        self.fixed_time = fixed_time
        self.required = required
        self.scheduled_time = None
        self.completed = False  # Tracks whether the task has been marked done
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"Invalid frequency: '{frequency}'. Must be one of {self.VALID_FREQUENCIES}")
        self.frequency = frequency  # None = one-off, "daily" or "weekly" = recurring

    def mark_complete(self) -> None:
        """Mark this task as completed"""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """
        Create a fresh, uncompleted copy of this task for the next occurrence.
        Only meaningful when frequency is "daily" or "weekly".

        Returns a new Task with the same attributes but completed=False and
        scheduled_time=None — ready to be added back to the pet and scheduled again.
        Raises ValueError if called on a one-off task (frequency=None).
        """
        if self.frequency is None:
            raise ValueError(f"'{self.title}' is a one-off task and has no next occurrence.")

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority_str,
            task_type=self.task_type,
            fixed_time=self.fixed_time,
            required=self.required,
            frequency=self.frequency
        )

    def get_priority_numeric(self) -> int:
        """Convert priority string to numeric value"""
        
        return self.priority_value
        
    
    def is_high_priority(self) -> bool:
        """Check if task is high priority"""
        
        return self.priority_str == "high"
        
    
    def is_fixed(self) -> bool:
        """ Check if task has a fixed time"""
        
        return self.task_type == "fixed" and self.fixed_time is not None 
        
        
    def can_schedule_at(self, start_hour: int, end_hour: int = None, owner_start: int = 0, owner_end: int = 24) -> bool:
        """
        Check if task can be scheduled at give time
        
        @param start_hour - hour to start the task
        @param end_hour - end hour (optional, will caluclate if not provided)
        @param owner_start - owner's available start hour
        @param owner_end - owner's available end hour
        @retrun - boolean indification if task fits
        """
        
        if end_hour is None:
            end_hour = start_hour + (self.duration_minutes / 60.0)
            
        if start_hour < owner_start or end_hour > owner_end:
            return False
            
        # check fixed time constraints
        if self.is_fixed():
            return start_hour == self.fixed_time
        
        # For flexible taks, return true
        return True
    
    def get_time_window(self, owner_start: int = 0, owner_end: int = 24) -> tuple:
        """
        Get available time window for flexible tasks.
        
        @param owner_start - owner's available start hour
        @param owner_end - owner's available end hour
        @return - (earlist_hour, latest_hour) tuple
        """
        
        if self.is_fixed():
            return (self.fixed_time, self.fixed_time)
        else:
            return (owner_start, owner_end)
    
    
    def update(self, title: str = None, duration_minutes: int = None, priority: str = None, task_type: str = None, fixed_time: int = None, required: bool = None) -> None:
        """Update task attributes"""
        
        if title is not None:
            self.title = title
            
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
            
        if priority is not None:
            
            # Validation
            if priority in self.PRIORITY_MAP:
                self.priority_str = priority
                self.priority_value = self.PRIORITY_MAP[priority]
            else:
                raise ValueError(f"Invalid priority: {priority}. Must be one of {list(self.PRIORITY_MAP.keys())}")
        
        if task_type is not None:
            self.task_type = task_type
            if task_type == "flexible":
                self.fixed_time = None
            elif task_type == "fixed" and self.fixed_time is None and fixed_time is None:
                raise ValueError("Cannot set task_type to 'fixed' without providing a fixed_time")

            
        if fixed_time is not None:
            
            if self.task_type == "fixed":
                self.fixed_time = fixed_time
   
            
        if required is not None:
            self.required = required

    
    def to_dict(self) -> dict:
        """Convert to dictionary for UI display"""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority_str,
            "task_type": self.task_type,
            "fixed_time": self.fixed_time,
            "required": self.required,
            "scheduled_time": self.scheduled_time,
            "completed": self.completed,
            "frequency": self.frequency
        }

    
    
    @classmethod
    def from_dict(cls, task_dict: dict):
        """Create Task from dictionary (for session state)"""
        task = cls(
            title=task_dict.get("title", ""),
            duration_minutes=task_dict.get("duration_minutes", 20),
            priority=task_dict.get("priority", "medium"),
            task_type=task_dict.get("task_type", "flexible"),
            fixed_time=task_dict.get("fixed_time"),
            required=task_dict.get("required", False),
            frequency=task_dict.get("frequency", None)
        )
        task.scheduled_time = task_dict.get("scheduled_time")
        task.completed = task_dict.get("completed", False)
        return task

    
    
    def __str__(self) -> str:
        """String representation for display"""
        priority_display = self.priority_str.upper()
        
        type_display = f"[{self.task_type}]" if self.task_type == "fixed" else ""
        
        required_display = " (REQUIRED)" if self.required else ""
        return f"{self.title} {type_display}{required_display} - {self.duration_minutes} min - {priority_display} priority"
    
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"Task(title='{self.title}', duration={self.duration_minutes}, priority='{self.priority_str}', type='{self.task_type}', fixed_time={self.fixed_time}, required={self.required})"
    
    
    def get_conflict_reasoning(self, conflicting_task) -> str:
        """
        Generate reasoning for why this task conflicts with another
        Used by scheduler for explanations
        """
        if self.priority_value > conflicting_task.priority_value:
            return f"'{self.title}' (priority {self.priority_str}) was scheduled over '{conflicting_task.title}' (priority {conflicting_task.priority_str}) due to higher priority"
        elif self.required and not conflicting_task.required:
            return f"'{self.title}' (required task) was scheduled over '{conflicting_task.title}' (optional) because it's mandatory"
        else:
            return f"'{self.title}' conflicts with '{conflicting_task.title}'"
    
    
    def get_scheduling_reasoning(self, scheduled_time: float) -> str:
        """
        Generate reasoning for why task was scheduled at specific time
        """
        # Convert decimal hour to HH:MM e.g. 8.1666... -> "08:10"
        hour = int(scheduled_time)
        minute = int(round((scheduled_time % 1) * 60))
        time_str = f"{hour:02d}:{minute:02d}"

        if self.is_fixed():
            return f"Task '{self.title}' must be done at {time_str} (fixed time requirement)"
        elif self.priority_value >= 4:
            return f"Task '{self.title}' was scheduled at {time_str} due to high priority ({self.priority_str})"
        else:
            return f"Task '{self.title}' was scheduled at {time_str} to fit within available time slots"
    