from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Task:
    title: str
    duration: int  # minutes
    priority: str  # "low" | "medium" | "high"
    category: str = ""
    frequency: str = "once"  # "once" | "daily" | "weekly"
    fixed_time: time | None = None
    completed: bool = False

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
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def pending_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass


@dataclass
class ScheduledItem:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class SkippedTask:
    task: Task
    reason: str = ""


@dataclass
class Plan:
    items: list[ScheduledItem] = field(default_factory=list)
    skipped: list[SkippedTask] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self, day: date) -> Plan:
        pass

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fit_to_time(self, tasks: list[Task], minutes: int) -> tuple[list[Task], list[Task]]:
        """Return (fits, doesn't fit) within the given minutes."""
        pass

    def find_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        pass
