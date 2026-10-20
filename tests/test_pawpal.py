from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Bingo", "Dog")
    assert len(pet.tasks_list) == 0

    pet.add_task(Task("Morning walk", 30, Priority.HIGH))

    assert len(pet.tasks_list) == 1
