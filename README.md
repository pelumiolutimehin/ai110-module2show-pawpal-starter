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

Run the full test suite from the project root:

```bash
python -m pytest
```

Sample output of a successful run:

```
ai110-module2show-pawpal-starter % python -m pytest
===================================================================== test session starts ======================================================================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/pelumiol/CodingWorkspace/CodePath-Coding-Workspace/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 26 items

tests/test_pawpal.py ..........................                                                                                                          [100%]

====================================================================== 26 passed in 0.02s ======================================================================
```

**Confidence Level:** ⭐⭐⭐⭐⭐ (5 stars)

Add `-v` to see each test by name. The suite lives in `tests/test_pawpal.py` (26 test cases) and covers:

| Area | What is verified |
|---|---|
| Basics | Marking a task complete changes its status; adding a task grows the pet's task list. |
| Sorting | `Scheduler.sort_by_time` returns tasks in chronological order, including midnight boundaries and unpadded hours (9:00 before 10:00); flexible tasks go last; ties break by priority; an empty list works; the input list is not mutated. |
| Recurrence | Completing a daily task creates one for the following day, and a weekly task one 7 days later; the new task keeps the original's details; month, year and leap-year rollovers are correct; one-off tasks create nothing; completing twice doesn't duplicate; late completion is never rescheduled into the past; unknown tasks raise `ValueError`. |
| Conflict detection | `Scheduler.conflict_warnings` flags duplicate times and partial overlaps, for the same pet and across different pets, with one warning per clashing pair; back-to-back, flexible and completed tasks are not flagged; empty and single-task schedules give no warnings. |
| Filtering | `Scheduler.filter_tasks` filters by pet (case-insensitive) and completion status, and returns an empty list for an unknown pet. |

## 📐 Smarter Scheduling

All methods are in `pawpal_system.py`, and `main.py` demonstrates each one.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time`, `Scheduler._sort_tasks` | `sort_by_time` orders tasks by `fixed_time`, earliest first, with flexible tasks last. Ties break by priority, then title. `_sort_tasks` is what `generate_plan` uses, ordering by priority and then shorter duration. |
| Filtering | `Scheduler.filter_tasks` | Keeps tasks by completion status (`completed=True/False`), pet name (case-insensitive), or both. It returns a new list, so it chains with `sort_by_time`. |
| Conflict detection | `Scheduler.find_conflicts`, `Scheduler.conflict_warnings`, `Scheduler._overlaps` | `_overlaps` compares time ranges, so back-to-back tasks don't clash. `find_conflicts` returns every overlapping pair, within one pet or across pets. `conflict_warnings` turns them into warning strings (empty list if none) instead of raising. |
| Recurring tasks | `Task.mark_complete`, `Pet.complete_task`, `Scheduler.complete_task` | Completing a daily or weekly task adds the next occurrence to the owning pet. The next due date is the previous due date + 1 or 7 days, not the completion date, and is never in the past. Completing a task twice does not create a duplicate. |

**Conflicts in a plan.** `Scheduler.generate_plan` also resolves fixed-time overlaps by keeping the higher-priority task and skipping the other with a reason, rather than moving it to a free slot.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
