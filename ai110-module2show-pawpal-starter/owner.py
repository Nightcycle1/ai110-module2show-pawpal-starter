class Owner:
    def __init__(self, name: str = "", available_hours_start: int = 8, available_hours_end: int = 20):
        """
        Initialize owner with name and default availability
        
        @param name - Owner's name
        @param available_hours_start - Hour (0-23) when owner is available (default 8am)
        @param available_hours_end - Hour (0-23) when owner stops being available (default 8pm)
        """
        self.name = name
        self.available_hours_start = available_hours_start
        self.available_hours_end = available_hours_end
        self.preferences = {} # For storing additional preferences
    
    
    def set_name(self, name: str) -> None:
        """Update owner name"""
        if not isinstance(name, str):
            raise ValueError("Name must be a string")

        
        self.name = name.strip()
    
    
    def set_available_hours(self, start: int, end: int) -> None:
        """
        Set available time window
     
        @param start - Start hour (0-23)
        @param end - End hour (0-23)
            
        @raises ValueError - If hours are invalid
        """
        # Validate hours
        if not (0 <= start <= 23):
            raise ValueError(f"Start hour must be between 0 and 23, got {start}")
        if not (0 <= end <= 23):
            raise ValueError(f"End hour must be between 0 and 23, got {end}")
        
        if start >= end:
            raise ValueError(f"Start hour ({start}) must be less than end hour ({end})")
        
        self.available_hours_start = start
        self.available_hours_end = end
    
    
    def get_available_minutes(self) -> int:
        """Calculate total available minutes: (end - start) * 60"""
        return (self.available_hours_end - self.available_hours_start) * 60
    
    
    def get_available_hours_range(self) -> tuple:
        """Return available hours as a tuple (start, end)"""
        return (self.available_hours_start, self.available_hours_end)
    
    
    def is_within_available_hours(self, start_hour: int, duration_minutes: int = 0) -> bool:
        """
        Check if a task fits within available hours
        
        @param start_hour - Hour when task would start
        @param duration_minutes - Duration of task in minutes
        
        @return - True if task fits within available hours
        """
        end_hour = start_hour + (duration_minutes / 60.0)
        
        return (start_hour >= self.available_hours_start and end_hour <= self.available_hours_end)
    
    
    def get_available_time_slots(self, task_duration: int) -> list:
        """
        Generate available time slots for a task of given duration
        
        @param task_duration: Duration in minutes
        
        @return - List of possible start hours (as integers) where task would fit
        """
        available_slots = []
        
        # Edge case
        if task_duration <= 0:
            return available_slots
                
        # Convert duration to hours for slot calculation
        duration_hours = task_duration / 60.0
        
        # Check each possible start hour
        for hour in range(self.available_hours_start, self.available_hours_end):
            end_hour = hour + duration_hours
            if end_hour <= self.available_hours_end:
                available_slots.append(hour)
        
        return available_slots
    
    
    def set_preference(self, key: str, value) -> None:
        """
        Set a preference (e.g., "morning_person": True, "prefer_walks_afternoon": True)
        
        @param key: Preference key
        @param value: Preference value
        """
        self.preferences[key] = value
    
    
    def get_preference(self, key: str, default=None):
        """Get a preference value"""
        return self.preferences.get(key, default)
    
    
    def update_preferences(self, **preferences) -> None:
        """Update multiple preferences at once"""
        self.preferences.update(preferences)
    
    
    def to_dict(self) -> dict:
        """Convert owner data to dictionary for session state"""
        return {
            "name": self.name,
            "available_hours_start": self.available_hours_start,
            "available_hours_end": self.available_hours_end,
            "preferences": self.preferences
        }
    
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Owner from dictionary (for session state)"""
        owner = cls(
            name=data.get("name", ""),
            available_hours_start=data.get("available_hours_start", 8),
            available_hours_end=data.get("available_hours_end", 20)
        )
        # Restore preferences
        if "preferences" in data:
            owner.preferences = data["preferences"]
        return owner
    
    
    def __str__(self) -> str:
        """String representation for display"""
        return (f"Owner: {self.name} (Available: {self.available_hours_start}:00 - "
                f"{self.available_hours_end}:00, {self.get_available_minutes()} minutes)")
    
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Owner(name='{self.name}', available_hours_start={self.available_hours_start}, "
                f"available_hours_end={self.available_hours_end}, preferences={self.preferences})")
    
    
    def get_schedule_summary(self) -> dict:
        """
        Get summary of owner's availability for display
        
        Returns:
            Dictionary with availability summary
        """
        return {
            "name": self.name,
            "available_start": self.available_hours_start,
            "available_end": self.available_hours_end,
            "total_minutes": self.get_available_minutes(),
            "total_hours": self.get_available_minutes() / 60
        }