from datetime import date, time

from pawpal_system import Task, Priority, Scheduler, Owner, Pet

launch_owner = Owner("John", 200)

first_pet = Pet("Bingo", "Dog", "German Shepherd")
second_pet = Pet("Valentine", "Cat", "Orange")

# Tasks are added deliberately out of time order, across both pets.
first_pet.add_task(Task("Evening feeding", 10, Priority.HIGH, "feeding", "daily", fixed_time=time(18, 0)))
second_pet.add_task(Task("Litter box cleaning", 15, Priority.MEDIUM, "hygiene", "daily", fixed_time=time(12, 15)))
first_pet.add_task(Task("Brush coat", 20, Priority.LOW, "grooming"))  # no fixed time
first_pet.add_task(Task("Morning walk", 30, Priority.HIGH, "exercise", "daily", fixed_time=time(7, 30)))
second_pet.add_task(Task("Play with feather toy", 15, Priority.LOW, "play", fixed_time=time(9, 0)))

launch_owner.add_pet(first_pet)
launch_owner.add_pet(second_pet)

today = date.today()
scheduler = Scheduler(launch_owner)
plan = scheduler.generate_plan(today)

# Complete one task so the completion filter has something to separate.
second_pet.complete_task(second_pet.tasks_list[0])


def show(heading: str, tasks: list[Task]) -> None:
    print(f"\n{heading}")
    print("-" * 50)
    for t in tasks:
        when = f"{t.fixed_time:%H:%M}" if t.fixed_time else "flexible"
        status = "done" if t.completed else "pending"
        print(f"{when:>8}  {t.title} ({t.pet_name}, {status})")
    if not tasks:
        print("(none)")


print(f"Today's Schedule for {launch_owner.name} ({today:%A, %B %d, %Y})")
print("=" * 50)
for item in plan.items:
    task = item.task
    print(f"{item.start_time:%H:%M} - {item.end_time:%H:%M}  {task.title} "
          f"({task.pet_name}, {task.priority.name.lower()} priority)")
for skipped in plan.skipped:
    print(f"Skipped: {skipped.task.title} ({skipped.task.pet_name}) - {skipped.reason}")

show("Added order (unsorted)", launch_owner.get_all_tasks())
show("Sorted by time", scheduler.sort_by_time())
show("Pending only", scheduler.filter_tasks(completed=False))
show("Completed only", scheduler.filter_tasks(completed=True))
show("Bingo's tasks", scheduler.filter_tasks(pet_name="Bingo"))
show("Valentine's pending tasks, by time",
     scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="valentine")))

# Conflict detection: two tasks at exactly the same time, once for the same pet
# (Bingo at 07:30) and once for different pets (Bingo and Valentine at 18:00).
first_pet.add_task(Task("Vet check-in", 30, Priority.MEDIUM, "health", fixed_time=time(7, 30)))
second_pet.add_task(Task("Grooming", 30, Priority.LOW, "grooming", fixed_time=time(18, 0)))

print("\nConflict check")
print("-" * 50)
for warning in scheduler.conflict_warnings(today) or ["No conflicts found."]:
    print(warning)

print(f"Today's Schedule for {launch_owner.name} ({today:%A, %B %d, %Y})")
print("=" * 50)
for item in plan.items:
    task = item.task
    print(f"{item.start_time:%H:%M} - {item.end_time:%H:%M}  {task.title} "
          f"({task.pet_name}, {task.priority.name.lower()} priority)")
for skipped in plan.skipped:
    print(f"Skipped: {skipped.task.title} ({skipped.task.pet_name}) - {skipped.reason}")
