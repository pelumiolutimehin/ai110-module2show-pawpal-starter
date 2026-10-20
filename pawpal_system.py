from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from enum import IntEnum

# Days until a task of each frequency recurs; None = does not recur.
_RECURRENCE_DAYS = {"once": None, "daily": 1, "weekly": 7}


class Priority(IntEnum):
    """Higher value = more important, so sorting descending puts HIGH first."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(eq=False)  # identity equality: two "Walk" tasks are still distinct
class Task:
    title: str
    duration: int  # minutes
    priority: Priority
    category: str = ""
    frequency: str = "once"  # "once" | "daily" | "weekly"
    fixed_time: time | None = None
    due_date: date | None = None  # None = due whenever not completed
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError("duration must be a positive number of minutes")
        if self.frequency not in _RECURRENCE_DAYS:
            raise ValueError(f"frequency must be one of {sorted(_RECURRENCE_DAYS)}")

    def mark_complete(self) -> Task | None:
        """Mark done; return the next occurrence if the task recurs.

        Recurrence follows a fixed schedule: the next due date is the current due
        date plus the interval (today if there is none), so completing a task late
        doesn't shift the cadence. It is never set in the past, so a task completed
        several days late doesn't come back already overdue.
        """
        self.completed = True
        interval = _RECURRENCE_DAYS[self.frequency]
        if interval is None:
            return None
        today = date.today()
        next_due = max((self.due_date or today) + timedelta(days=interval), today)
        return replace(self, completed=False, due_date=next_due)

    def is_due(self, day: date) -> bool:
        """A task is due on `day` if it is not completed and its due date has arrived."""
        return not self.completed and (self.due_date is None or self.due_date <= day)


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks_list: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task and stamp it with this pet's name."""
        task.pet_name = self.name
        self.tasks_list.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task (matched by identity); raises ValueError if it isn't this pet's."""
        self.tasks_list.remove(task)

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and add its next occurrence, if any."""
        if task not in self.tasks_list:
            raise ValueError(f"{task.title!r} is not one of {self.name}'s tasks")
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)

    def pending_tasks(self) -> list[Task]:
        """Tasks that have not been completed yet."""
        return [t for t in self.tasks_list if not t.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet; names must be unique since tasks are tagged by pet name."""
        if any(p.name.lower() == pet.name.lower() for p in self.pets):
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}")
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet (matched by identity); raises ValueError if it isn't theirs."""
        for i, p in enumerate(self.pets):
            if p is pet:
                del self.pets[i]
                return
        raise ValueError(f"{pet.name!r} is not one of {self.name}'s pets")

    def get_all_tasks(self) -> list[Task]:
        """Every task across all pets, grouped by pet in the order pets were added."""
        return [task for pet in self.pets for task in pet.tasks_list]


@dataclass
class ScheduledItem:
    task: Task
    start_time: datetime
    end_time: datetime
    reason: str = ""


@dataclass
class SkippedTask:
    task: Task
    reason: str = ""


@dataclass
class Plan:
    items: list[ScheduledItem] = field(default_factory=list)
    skipped: list[SkippedTask] = field(default_factory=list)

    @property
    def total_minutes(self) -> int:
        pass

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_due_tasks(self, day: date) -> list[Task]:
        """Tasks due on `day`, gathered across all of the owner's pets."""
        return [t for t in self.owner.get_all_tasks() if t.is_due(day)]

    def generate_plan(self, day: date) -> Plan:
        """Place fixed-time tasks first, then fill gaps with flexible tasks."""
        due = self._sort_tasks(self.get_due_tasks(day))
        fixed = [t for t in due if t.fixed_time is not None]
        flexible = [t for t in due if t.fixed_time is None]
        plan = Plan()

        # Fixed-time tasks: the higher-priority task wins any overlap.
        kept: list[Task] = []
        for task in fixed:
            clash = next((k for k in kept if self._overlaps(k, task)), None)
            if clash is None:
                kept.append(task)
            else:
                plan.skipped.append(SkippedTask(
                    task, f"Overlaps '{clash.title}' ({clash.pet_name}), which has higher priority"))

        fits, over = self._fit_to_time(kept, self.owner.available_minutes)
        plan.skipped.extend(SkippedTask(t, "Not enough available time") for t in over)
        for task in fits:
            start = datetime.combine(day, task.fixed_time)
            plan.items.append(ScheduledItem(
                task, start, start + timedelta(minutes=task.duration),
                f"Fixed time {task.fixed_time:%H:%M}"))

        # Flexible tasks: fit the remaining minutes, then place each in the earliest gap.
        remaining = self.owner.available_minutes - sum(t.duration for t in fits)
        fits, over = self._fit_to_time(flexible, remaining)
        plan.skipped.extend(SkippedTask(t, "Not enough available time") for t in over)
        for task in fits:
            start = self._earliest_gap(plan.items, datetime.combine(day, self.owner.day_start),
                                       task.duration)
            plan.items.append(ScheduledItem(
                task, start, start + timedelta(minutes=task.duration),
                f"{task.priority.name.title()} priority, placed in the earliest free slot"))

        plan.items.sort(key=lambda item: item.start_time)
        return plan

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by priority (descending); shorter tasks first within a priority."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

    def _fit_to_time(self, tasks: list[Task], minutes: int) -> tuple[list[Task], list[Task]]:
        """Return (fits, doesn't fit); keep trying shorter tasks after one misses."""
        fits: list[Task] = []
        over: list[Task] = []
        for task in tasks:
            if task.duration <= minutes:
                fits.append(task)
                minutes -= task.duration
            else:
                over.append(task)
        return fits, over

    def find_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Pairs of fixed-time tasks whose time ranges overlap, across all pets."""
        timed = [t for t in tasks if t.fixed_time is not None]
        return [(a, b) for i, a in enumerate(timed) for b in timed[i + 1:]
                if self._overlaps(a, b)]

    @staticmethod
    def _overlaps(a: Task, b: Task) -> bool:
        """True if two fixed-time tasks overlap (back-to-back is not an overlap)."""
        def span(t: Task) -> tuple[int, int]:
            start = t.fixed_time.hour * 60 + t.fixed_time.minute
            return start, start + t.duration
        (a_start, a_end), (b_start, b_end) = span(a), span(b)
        return a_start < b_end and b_start < a_end

    @staticmethod
    def _earliest_gap(items: list[ScheduledItem], start: datetime, minutes: int) -> datetime:
        """First time at or after `start` where `minutes` fit between scheduled items."""
        length = timedelta(minutes=minutes)
        for item in sorted(items, key=lambda i: i.start_time):
            if item.end_time <= start:
                continue
            if start + length <= item.start_time:
                break
            start = item.end_time
        return start
