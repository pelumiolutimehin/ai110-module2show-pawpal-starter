from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import IntEnum


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

    def mark_complete(self) -> Task | None:
        """Mark done; return the next occurrence if the task recurs."""
        pass

    def is_due(self, day: date) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks_list: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task and stamp it with this pet's name."""
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and add its next occurrence, if any."""
        pass

    def pending_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass


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

    def generate_plan(self, day: date) -> Plan:
        """Place fixed-time tasks first, then fill gaps with flexible tasks."""
        pass

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by priority (descending)."""
        pass

    def _fit_to_time(self, tasks: list[Task], minutes: int) -> tuple[list[Task], list[Task]]:
        """Return (fits, doesn't fit); keep trying shorter tasks after one misses."""
        pass

    def find_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        pass
