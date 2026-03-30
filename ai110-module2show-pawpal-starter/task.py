class Task:
    # Priority mapping for UI (low, medium, high) to numeric values
    PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}
    
    def __init__(self, title: str = "", duration_minutes: int = 20, 
                 priority: str = "medium", task_type: str = "flexible", 
                 fixed_time: int = None, required: bool = False):
        """
        Initialize task with attributes matching UI inputs
        Args:
            title: Task name (from UI)
            duration_minutes: Duration in minutes (from UI)
            priority: "low", "medium", or "high" (from UI)
            task_type: "flexible" or "fixed"
            fixed_time: Hour (0-23) if fixed
            required: Whether task is mandatory
        """
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority_str = priority
        self.priority_value = self.PRIORITY_MAP.get(priority, 3)
        self.task_type = task_type
        self.fixed_time = fixed_time
        self.required = required
        self.scheduled_time = None
    
    def get_priority_numeric(self) -> int:
        """Convert priority string to numeric value"""
        pass
    
    def is_high_priority(self) -> bool:
        """Check if task is high priority"""
        pass
    
    def update(self, title: str = None, duration_minutes: int = None, 
               priority: str = None) -> None:
        """Update task attributes"""
        pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary for UI display"""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority_str
        }
    
    @classmethod
    def from_dict(cls, task_dict: dict):
        """Create Task from dictionary (for session state)"""
        return cls(
            title=task_dict["title"],
            duration_minutes=task_dict["duration_minutes"],
            priority=task_dict["priority"]
        )