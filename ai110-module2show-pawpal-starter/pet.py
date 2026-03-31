from typing import List, Dict, Any
from task import Task



class Pet:
    """
    Represents a pet with its basic information and associated care tasks.
    
    The Pet class manages the pet's identity (name, species, age) and
    maintains a collection of tasks that need to be performed for this pet.
    """    
    
    # Class-level constants for valid species
    VALID_SPECIES = ["dog", "cat", "bird", "rabbit", "hamster", "other"]
    
    
    def __init__(self, name: str = "", species: str = "dog", age: int = 1):
        """
        Initialize pet with basic info
        
        @param name - Pet's name
        @param species - Type of pet (dog, cat, etc.)
        @param age - Age in years
        """
        self.name = name
        self.species = species
        self.age = age
        self.tasks: List[Task] = [] # List to store task objects
        self.notes: str = "" # Optional notes about the pet
    
    
    def set_name(self, name: str) -> None:
        """Update pet name with validation"""
        
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        
        self.name = name.strip()
    
    
    def set_species(self, species: str) -> str:
        """Update pet species with validation"""
        species_lower = species.lower().strip()
        
        if species_lower not in self.VALID_SPECIES:
            # Allow custom species but warn (or raise error depending on requirements)
            # For flexibility, we'll allow any string but store normalized version
            self.species = species_lower
            return f"Note: '{species}' is not a standard species"
        
        self.species = species_lower
        return ""
    
    
    def set_age(self, age: int) -> None:
        """Update pet age with validation"""
        if not isinstance(age, int) or age < 0:
            raise ValueError(f"Age must be a non-negative integer, got {age}")
        
        self.age = age
        
        
    def set_notes(self, notes: str) -> None:
        """Update pet notes/special needs"""
        if not isinstance(notes, str):
            raise ValueError("Notes must be a string")
        
        self.notes = notes.strip()

    
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to this pet's care routine
        
        @param task - Task object to add
            
        @raises ValueError - If task is not a Task instance
        """
        if not isinstance(task, Task):
            raise ValueError(f"Expected Task object, got {type(task)}")
        
        self.tasks.append(task)
    
    
    def remove_task(self, task_index: int) -> Task:
        """
        Remove task by index
        
        @param task_index: Index of task to remove
            
        @return - The removed Task object, or None if index is invalid
        """
        if not (0 <= task_index < len(self.tasks)):
            raise IndexError(f"Task index {task_index} is out of range (0-{len(self.tasks)-1})")
        
        return self.tasks.pop(task_index)
    
    def remove_task_by_title(self, title: str) -> bool:
        """
        Remove task by title (removes first matching)
        
        @param title - Title of task to remove
            
        @return - True if task was removed, False if not found
        """
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        
        return False
    
    
    def get_tasks(self) -> List[Task]:
        """Return list of tasks"""
        return self.tasks.copy()  # Return a copy to prevent external modification
    
    
    def get_task_count(self) -> int:
        """Return number of tasks"""
        return len(self.tasks)
    
    
    def get_total_task_time(self) -> int:
        """Calculate total minutes for all tasks"""
        return sum(task.duration_minutes for task in self.tasks)
    
    
    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority (highest first)"""
        # Create a copy of tasks to avoid modifying the original list
        sorted_tasks = self.tasks.copy()
    
        # Sort by priority_value in descending order (highest first)
        sorted_tasks.sort(key=lambda task: task.priority_value, reverse=True)
        
        return sorted_tasks
    
    
    def get_fixed_time_tasks(self) -> List[Task]:
        """Return tasks that have fixed times"""
        return [task for task in self.tasks if task.is_fixed()]
    
    
    def get_flexible_tasks(self) -> List[Task]:
        """Return tasks that are flexible"""
        return [task for task in self.tasks if not task.is_fixed()]
    
    
    def get_required_tasks(self) -> List[Task]:
        """Return required (mandatory) tasks"""
        return [task for task in self.tasks if task.required]
    
    
    def get_optional_tasks(self) -> List[Task]:
        """Return optional tasks"""
        return [task for task in self.tasks if not task.required]
    
    
    def clear_tasks(self) -> None:
        """Remove all tasks"""
        self.tasks.clear()
    
    
    def update_task(self, task_index: int, **kwargs) -> bool:
        """
        Update a task by index
        
        @param task_index - Index of task to update
        @param **kwargs - Attributes to update (title, duration_minutes, priority, etc.)
            
        @return - True if update was successful, False if index invalid
        """
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].update(**kwargs)
            return True
        
        return False
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pet data to dictionary for session state
        
        @return - Dictionary with all pet data including serialized tasks
        """
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "notes": self.notes,
            "tasks": [task.to_dict() for task in self.tasks]  # Serialize each task
        }
    
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pet':
        """
        Create Pet from dictionary (for session state restoration)
        
        @param data: Dictionary with pet data
            
        @return - Pet instance with restored tasks
        """
        pet = cls(
            name=data.get("name", ""),
            species=data.get("species", "dog"),
            age=data.get("age", 1)
        )
        
        # Restore notes if present
        pet.notes = data.get("notes", "")
        
        # Restore tasks if present
        if "tasks" in data:
            for task_dict in data["tasks"]:
                task = Task.from_dict(task_dict)
                pet.add_task(task)
        
        return pet
    
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        task_count = len(self.tasks)
        total_time = self.get_total_task_time()
        return (f"{self.name} ({self.species}, {self.age} year{'s' if self.age != 1 else ''}) - "
                f"{task_count} task{'s' if task_count != 1 else ''}, "
                f"{total_time} total minutes")
    
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Pet(name='{self.name}', species='{self.species}', age={self.age}, "f"tasks={len(self.tasks)}, notes='{self.notes}')")
    
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of pet's care requirements"""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "total_tasks": self.get_task_count(),
            "total_time_minutes": self.get_total_task_time(),
            "fixed_tasks": len(self.get_fixed_time_tasks()),
            "required_tasks": len(self.get_required_tasks()),
            "high_priority_tasks": len([t for t in self.tasks if t.is_high_priority()])
        }