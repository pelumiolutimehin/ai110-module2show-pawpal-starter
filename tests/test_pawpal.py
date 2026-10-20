from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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


def _owner_with_task(frequency, due_date=None):
    owner = Owner("John", 200)
    pet = Pet("Bingo", "Dog")
    owner.add_pet(pet)
    task = Task("Walk", 30, Priority.HIGH, frequency=frequency, due_date=due_date)
    pet.add_task(task)
    return owner, pet, task


@pytest.mark.parametrize("frequency, days", [("daily", 1), ("weekly", 7)])
def test_completing_recurring_task_creates_next_occurrence(frequency, days):
    owner, pet, task = _owner_with_task(frequency, due_date=date.today())

    next_task = Scheduler(owner).complete_task(task)

    assert task.completed is True
    assert next_task is not task and next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=days)
    assert next_task.pet_name == "Bingo"
    assert next_task in pet.tasks_list and len(pet.tasks_list) == 2


def test_completing_one_off_task_creates_nothing():
    owner, pet, task = _owner_with_task("once")

    assert Scheduler(owner).complete_task(task) is None
    assert len(pet.tasks_list) == 1


def test_completing_twice_does_not_duplicate_occurrence():
    owner, pet, task = _owner_with_task("daily", due_date=date.today())
    scheduler = Scheduler(owner)

    scheduler.complete_task(task)
    assert scheduler.complete_task(task) is None
    assert len(pet.tasks_list) == 2


def test_late_completion_keeps_cadence_but_never_in_past():
    owner, _, task = _owner_with_task("daily", due_date=date.today() - timedelta(days=5))

    assert Scheduler(owner).complete_task(task).due_date == date.today()


def test_scheduler_complete_task_rejects_unknown_task():
    owner, _, _ = _owner_with_task("daily")

    with pytest.raises(ValueError):
        Scheduler(owner).complete_task(Task("Stranger", 5, Priority.LOW))


def _clash_owner():
    owner = Owner("John", 300)
    dog, cat = Pet("Bingo", "Dog"), Pet("Valentine", "Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat


def test_conflict_warning_for_same_pet_overlap():
    owner, dog, _ = _clash_owner()
    dog.add_task(Task("Walk", 30, Priority.HIGH, fixed_time=time(7, 30)))
    dog.add_task(Task("Bath", 30, Priority.LOW, fixed_time=time(7, 45)))

    warnings = Scheduler(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "same pet (Bingo)" in warnings[0] and "07:30-08:00" in warnings[0]


def test_conflict_warning_for_different_pets_at_same_time():
    owner, dog, cat = _clash_owner()
    dog.add_task(Task("Walk", 30, Priority.HIGH, fixed_time=time(9, 0)))
    cat.add_task(Task("Vet", 30, Priority.HIGH, fixed_time=time(9, 0)))

    warnings = Scheduler(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "different pets" in warnings[0]
    assert "Bingo" in warnings[0] and "Valentine" in warnings[0]


def test_back_to_back_and_flexible_tasks_do_not_conflict():
    owner, dog, cat = _clash_owner()
    dog.add_task(Task("Walk", 30, Priority.HIGH, fixed_time=time(9, 0)))
    cat.add_task(Task("Feed", 15, Priority.HIGH, fixed_time=time(9, 30)))
    cat.add_task(Task("Brush", 20, Priority.LOW))

    assert Scheduler(owner).conflict_warnings() == []


def test_completed_tasks_are_ignored_by_conflict_warnings():
    owner, dog, cat = _clash_owner()
    walk = Task("Walk", 30, Priority.HIGH, fixed_time=time(9, 0))
    dog.add_task(walk)
    cat.add_task(Task("Vet", 30, Priority.HIGH, fixed_time=time(9, 0)))
    walk.completed = True

    assert Scheduler(owner).conflict_warnings() == []


# --- Sorting ---------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    owner, dog, cat = _clash_owner()
    dog.add_task(Task("Dinner", 20, Priority.HIGH, fixed_time=time(18, 0)))
    cat.add_task(Task("Breakfast", 10, Priority.HIGH, fixed_time=time(7, 0)))
    dog.add_task(Task("Lunch", 10, Priority.HIGH, fixed_time=time(12, 30)))

    ordered = Scheduler(owner).sort_by_time()

    assert [t.title for t in ordered] == ["Breakfast", "Lunch", "Dinner"]


def test_sort_by_time_handles_midnight_boundaries_and_unpadded_hours():
    owner, dog, _ = _clash_owner()
    dog.add_task(Task("Late", 5, Priority.LOW, fixed_time=time(23, 59)))
    dog.add_task(Task("Ten", 5, Priority.LOW, fixed_time=time(10, 0)))
    dog.add_task(Task("Nine", 5, Priority.LOW, fixed_time=time(9, 0)))
    dog.add_task(Task("Midnight", 5, Priority.LOW, fixed_time=time(0, 0)))

    titles = [t.title for t in Scheduler(owner).sort_by_time()]

    assert titles == ["Midnight", "Nine", "Ten", "Late"]  # 9:00 before 10:00


def test_sort_by_time_puts_flexible_tasks_last_and_breaks_ties_by_priority():
    owner, dog, cat = _clash_owner()
    dog.add_task(Task("Flexible", 10, Priority.HIGH))
    dog.add_task(Task("Low tie", 10, Priority.LOW, fixed_time=time(9, 0)))
    cat.add_task(Task("High tie", 10, Priority.HIGH, fixed_time=time(9, 0)))

    titles = [t.title for t in Scheduler(owner).sort_by_time()]

    assert titles == ["High tie", "Low tie", "Flexible"]


def test_sort_by_time_empty_and_does_not_mutate_input():
    assert Scheduler(Owner("John", 60)).sort_by_time() == []

    owner, dog, _ = _clash_owner()
    late = Task("Late", 5, Priority.LOW, fixed_time=time(20, 0))
    early = Task("Early", 5, Priority.LOW, fixed_time=time(6, 0))
    original = [late, early]

    result = Scheduler(owner).sort_by_time(original)

    assert result == [early, late]
    assert original == [late, early]


# --- Recurrence ------------------------------------------------------------

def test_completing_daily_task_creates_task_for_following_day():
    owner, pet, task = _owner_with_task("daily", due_date=date.today())

    next_task = Scheduler(owner).complete_task(task)

    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.frequency == "daily"


def test_next_occurrence_inherits_task_details():
    owner, pet, task = _owner_with_task("daily", due_date=date.today())
    task.fixed_time = time(7, 30)
    task.category = "exercise"

    next_task = Scheduler(owner).complete_task(task)

    assert (next_task.title, next_task.duration, next_task.priority) == ("Walk", 30, Priority.HIGH)
    assert (next_task.fixed_time, next_task.category) == (time(7, 30), "exercise")


@pytest.mark.parametrize("due, expected", [
    (date(2100, 12, 31), date(2101, 1, 1)),    # year rollover
    (date(2100, 1, 31), date(2100, 2, 1)),     # month rollover
    (date(2096, 2, 28), date(2096, 2, 29)),    # leap year
    (date(2100, 2, 28), date(2100, 3, 1)),     # non-leap year
])
def test_daily_recurrence_rolls_over_month_year_and_leap_boundaries(due, expected):
    owner, _, task = _owner_with_task("daily", due_date=due)

    assert Scheduler(owner).complete_task(task).due_date == expected


# --- Conflict detection ----------------------------------------------------

def test_scheduler_flags_duplicate_times_for_same_pet():
    owner, dog, _ = _clash_owner()
    dog.add_task(Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0)))
    dog.add_task(Task("Bath", 30, Priority.LOW, fixed_time=time(8, 0)))

    warnings = Scheduler(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "same pet (Bingo)" in warnings[0]
    assert "08:00-08:30" in warnings[0]


def test_three_tasks_at_same_time_produce_a_warning_per_pair():
    owner, dog, cat = _clash_owner()
    dog.add_task(Task("A", 30, Priority.HIGH, fixed_time=time(8, 0)))
    dog.add_task(Task("B", 30, Priority.HIGH, fixed_time=time(8, 0)))
    cat.add_task(Task("C", 30, Priority.HIGH, fixed_time=time(8, 0)))

    assert len(Scheduler(owner).conflict_warnings()) == 3


def test_no_tasks_or_single_task_has_no_conflicts():
    assert Scheduler(Owner("John", 60)).conflict_warnings() == []

    owner, dog, _ = _clash_owner()
    dog.add_task(Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0)))
    assert Scheduler(owner).conflict_warnings() == []


# --- Filtering -------------------------------------------------------------

def test_filter_tasks_by_pet_and_completion():
    owner, dog, cat = _clash_owner()
    walk, feed = Task("Walk", 30, Priority.HIGH), Task("Feed", 10, Priority.HIGH)
    dog.add_task(walk)
    cat.add_task(feed)
    walk.completed = True
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="bingo") == [walk]  # case-insensitive
    assert scheduler.filter_tasks(completed=False) == [feed]
    assert scheduler.filter_tasks(completed=True, pet_name="Valentine") == []
    assert scheduler.filter_tasks(pet_name="Nobody") == []
