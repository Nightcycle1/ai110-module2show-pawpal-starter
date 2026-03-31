import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'ai110-module2show-pawpal-starter'))

from task import Task
from pet import Pet



def test_mark_complete_changes_status():
    """
    Task Completion: Verify that calling mark_complete() actually changes the task's status.

    Before calling mark_complete(), completed should be False (default).
    After calling it, completed should be True.
    This confirms the method actually mutates the task's state.
    """
    task = Task(title="Morning Walk", duration_minutes=30, priority="high")

    # Should start as incomplete
    assert task.completed == False

    task.mark_complete()

    # Should now be marked done
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    """
    Task Addition: Verify that adding a task to a Pet increases that pet's task count.

    Start with a fresh pet (0 tasks), add one task, check count is 1.
    Add a second task, check count is 2.
    This confirms add_task() actually appends to the pet's task list.
    """
    pet = Pet(name="Mochi", species="dog", age=3)

    # Fresh pet should have no tasks
    assert pet.get_task_count() == 0

    pet.add_task(Task(title="Feeding", duration_minutes=15, priority="high"))
    assert pet.get_task_count() == 1

    pet.add_task(Task(title="Walk", duration_minutes=30, priority="medium"))
    assert pet.get_task_count() == 2
