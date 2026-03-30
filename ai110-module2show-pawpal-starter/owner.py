class Owner:
    def __init__(self, name: str = "", available_hours_start: int = 8, available_hours_end: int = 20):
        """Initialize owner with name and default availability"""
        self.name = name
        self.available_hours_start = available_hours_start
        self.available_hours_end = available_hours_end
    
    def set_name(self, name: str) -> None:
        """Update owner name"""
        pass
    
    def set_available_hours(self, start: int, end: int) -> None:
        """Set available time window"""
        pass
    
    def get_available_minutes(self) -> int:
        """Calculate total available minutes: (end - start) * 60"""
        pass
    
    def to_dict(self) -> dict:
        """Convert owner data to dictionary for session state"""
        pass