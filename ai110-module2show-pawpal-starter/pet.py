class Pet:
    def __init__(self, name: str = "", species: str = "dog", age: int = 1):
        """Initialize pet with basic info"""
        self.name = name
        self.species = species
        self.age = age
        self.tasks = []
    
    def set_name(self, name: str) -> None:
        """Update pet name"""
        pass
    
    def set_species(self, species: str) -> None:
        """Update pet species"""
        pass
    
    def add_task(self, task) -> None:
        """Add a task to this pet's care routine"""
        pass
    
    def remove_task(self, task_index: int) -> None:
        """Remove task by index"""
        pass
    
    def get_tasks(self) -> list:
        """Return list of tasks"""
        pass
    
    def to_dict(self) -> dict:
        """Convert pet data to dictionary for session state"""
        pass