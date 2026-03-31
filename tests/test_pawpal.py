import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'ai110-module2show-pawpal-starter'))

from task import Task
from pet import Pet
from owner import Owner
from scheduler import Scheduler


def test_mark_complete_changes_status():
    """Verify mark_complete() changes task status"""
    task = Task(title="Walk", duration_minutes=30, priority="high")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_count():
    """Adding tasks increases pet's task count"""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert pet.get_task_count() == 0
    pet.add_task(Task(title="Feed", duration_minutes=15, priority="high"))
    assert pet.get_task_count() == 1


def test_remove_task_decreases_count():
    """Removing tasks decreases pet's task count"""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(title="Feed", duration_minutes=15, priority="high")
    pet.add_task(task)
    assert pet.get_task_count() == 1
    pet.remove_task(0)
    assert pet.get_task_count() == 0


def test_total_duration_calculation():
    """Pet correctly sums task durations"""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Feed", duration_minutes=15, priority="high"))
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="medium"))
    total = sum(task.duration_minutes for task in pet.get_tasks())
    assert total == 45


def test_sorting_by_chronological_order():
    """Tasks should be scheduled in chronological order"""
    owner = Owner(name="John", available_hours_start=8, available_hours_end=20)
    pet = Pet(name="Mochi", species="dog", age=3)
    
    pet.add_task(Task(title="Evening Walk", duration_minutes=30, 
                      task_type="fixed", fixed_time=19))
    pet.add_task(Task(title="Morning Walk", duration_minutes=30, 
                      task_type="fixed", fixed_time=8))
    
    scheduler = Scheduler(owner, pet)
    result = scheduler.generate_plan()
    
    scheduled = result["scheduled"]
    assert scheduled[0].start_time == 8
    assert scheduled[1].start_time == 19


def test_recurrence_logic_daily():
    """Marking a daily task complete creates a new task"""
    owner = Owner(name="John", available_hours_start=8, available_hours_end=20)
    pet = Pet(name="Mochi", species="dog", age=3)
    
    daily_task = Task(
        title="Daily Walk",
        duration_minutes=30,
        priority="high",
        frequency="daily"
    )
    pet.add_task(daily_task)
    assert pet.get_task_count() == 1
    
    scheduler = Scheduler(owner, pet)
    new_task = scheduler.mark_task_complete(daily_task)
    
    assert new_task is not None
    assert new_task.completed == False
    assert pet.get_task_count() == 2


def test_recurrence_one_off():
    """One-off tasks don't create new instances"""
    owner = Owner(name="John", available_hours_start=8, available_hours_end=20)
    pet = Pet(name="Mochi", species="dog", age=3)
    
    one_off = Task(
        title="One Time Walk",
        duration_minutes=30,
        priority="medium",
        frequency=None
    )
    pet.add_task(one_off)
    
    scheduler = Scheduler(owner, pet)
    result = scheduler.mark_task_complete(one_off)
    
    assert result is None
    assert pet.get_task_count() == 1


def test_conflict_detection_duplicate_times():
    """Duplicate fixed times should be flagged as conflicts"""
    owner = Owner(name="John", available_hours_start=8, available_hours_end=20)
    pet = Pet(name="Mochi", species="dog", age=3)
    
    pet.add_task(Task(title="Walk", duration_minutes=30, 
                      task_type="fixed", fixed_time=9))
    pet.add_task(Task(title="Feed", duration_minutes=20, 
                      task_type="fixed", fixed_time=9))
    
    scheduler = Scheduler(owner, pet)
    result = scheduler.generate_plan()
    
    # One task should be unscheduled due to conflict
    assert len(result["unscheduled"]) == 1
    assert any("conflict" in r.lower() for r in result["reasoning"])


def test_conflict_detection_across_pets():
    """Conflicts should be detected across multiple pets"""
    owner = Owner(name="John", available_hours_start=8, available_hours_end=20)
    
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet1.add_task(Task(title="Walk", duration_minutes=60, 
                       task_type="fixed", fixed_time=9))
    
    pet2 = Pet(name="Luna", species="cat", age=2)
    pet2.add_task(Task(title="Feed", duration_minutes=30, 
                       task_type="fixed", fixed_time=9))
    
    scheduler1 = Scheduler(owner, pet1)
    scheduler2 = Scheduler(owner, pet2)
    scheduler1.generate_plan()
    scheduler2.generate_plan()
    
    conflicts = scheduler1.detect_conflicts(scheduler2.schedule)
    assert len(conflicts) >= 1