# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The core domain logic is in `pawpal_system.py` and can be exercised from the CLI via `main.py`. The Streamlit UI (`app.py`) is not yet connected.

**Data model.** `Owner` aggregates `Pet`s, and each `Pet` aggregates its own `Task`s (`Owner → Pet → Task`). `Task` carries `duration`, a `Priority` (`IntEnum`), `frequency` (`once`/`daily`/`weekly`), an optional `fixed_time`, and an optional `due_date`. `Task.is_due(day)` returns true for incomplete tasks whose due date has arrived. `Task.mark_complete()` returns the next occurrence for recurring tasks, and `Pet.complete_task()` appends it to the pet's list. `Task` uses identity equality (`eq=False`), so two tasks with the same title remain distinct.

**Scheduling.** `Scheduler` reads from `Owner.get_all_tasks()` rather than any single pet, so tasks from every pet compete for the same time budget. `generate_plan(day)` filters to due tasks, sorts them by priority (shorter first within a priority), and builds a `Plan` in three steps:

1. Fixed-time tasks are placed first. Overlaps are detected with an interval check (`a.start < b.end and b.start < a.end`), and the lower-priority task in a conflict is skipped.
2. Remaining flexible tasks are fitted greedily against the minutes left after the fixed tasks (`available_minutes` minus fixed durations). A task that doesn't fit is skipped, and shorter tasks after it are still considered.
3. Each flexible task is placed in the earliest free gap at or after `Owner.day_start`.

Unscheduled tasks are recorded as `SkippedTask`s with a reason string. `Plan.explain()` and `Plan.total_minutes` are not implemented yet, so `main.py` formats the output directly from `plan.items`.

**Design decisions.**
- Recurrence follows a fixed schedule: the next due date is the previous due date plus the interval (or today if none), clamped to never fall in the past. It is not relative to the completion date.
- Pet names must be unique per owner, since `Pet.add_task` stamps each task with `pet_name`.

## 🖥️ Sample Output

Output from running `python main.py`:

```
(.venv) pelumiol@Oluwapelumis-MacBook-Pro-2 ai110-module2show-pawpal-starter % python main.py
Today's Schedule for John (Tuesday, October 20, 2026)
==================================================
07:30 - 08:00  Morning walk (Bingo, high priority)
12:15 - 12:30  Litter box cleaning (Valentine, medium priority)
18:00 - 18:10  Evening feeding (Bingo, high priority)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | `Task.mark_complete`, `Pet.complete_task` | Daily/weekly tasks follow a fixed schedule: the next due date is the previous due date + 1 or 7 days, not the completion date. It is never set in the past, so a late completion doesn't create an overdue task. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
