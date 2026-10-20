from datetime import date, time

from pawpal_system import Task, Priority, Scheduler, Owner, Pet

launch_owner = Owner("John", 200)

first_pet = Pet("Bingo", "Dog", "German Shepherd")
second_pet = Pet("Valentine", "Cat", "Orange")

first_pet.add_task(Task("Morning walk", 30, Priority.HIGH, "exercise", "daily", fixed_time=time(7, 30)))
first_pet.add_task(Task("Evening feeding", 10, Priority.HIGH, "feeding", "daily", fixed_time=time(18, 0)))
second_pet.add_task(Task("Litter box cleaning", 15, Priority.MEDIUM, "hygiene", "daily", fixed_time=time(12, 15)))

launch_owner.add_pet(first_pet)
launch_owner.add_pet(second_pet)

today = date.today()
plan = Scheduler(launch_owner).generate_plan(today)

print(f"Today's Schedule for {launch_owner.name} ({today:%A, %B %d, %Y})")
print("=" * 50)
for item in plan.items:
    task = item.task
    print(f"{item.start_time:%H:%M} - {item.end_time:%H:%M}  {task.title} "
          f"({task.pet_name}, {task.priority.name.lower()} priority)")
for skipped in plan.skipped:
    print(f"Skipped: {skipped.task.title} ({skipped.task.pet_name}) - {skipped.reason}")
