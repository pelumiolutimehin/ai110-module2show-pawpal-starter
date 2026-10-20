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

## ✨ Features

- **Priority-based planning.** Tasks due on a day are ordered by priority (high first), then by shorter duration. Higher-priority tasks get time first.
- **Fixed-time placement.** Tasks with a set time are placed first, and flexible tasks fill the free gaps from the owner's day start. Each flexible task goes in the earliest slot where it fits.
- **Time-budget fitting.** Tasks are added until the owner's available minutes run out. A task that doesn't fit is skipped, and shorter ones after it are still tried.
- **Sorting by time.** `sort_by_time` orders tasks chronologically, with flexible tasks last. Ties are broken by priority, then title, and the original list is left unchanged.
- **Filtering.** `filter_tasks` keeps tasks by completion status, pet name (case-insensitive), or both. It returns a new list, so the result can be sorted.
- **Conflict warnings.** `conflict_warnings` finds fixed-time tasks whose time ranges overlap, within one pet or across pets, and returns readable messages instead of raising. Back-to-back and completed tasks are not flagged.
- **Conflict resolution.** When fixed-time tasks overlap, `generate_plan` keeps the higher-priority one. The other is listed as skipped with the reason.
- **Daily and weekly recurrence.** Completing a recurring task creates the next occurrence, due 1 or 7 days after the previous due date. The new task keeps the same title, duration, priority, category and fixed time.
- **Fixed recurrence schedule.** The next due date follows the old due date, not the completion date, and is never in the past. A task completed late doesn't come back overdue.

- **Skip reasons.** Every task left out of a plan is recorded with a reason, such as an overlap or not enough available time.

## 🛠️ Implementation Summary

The core domain logic is in `pawpal_system.py` and can be exercised from the CLI via `main.py`. The Streamlit UI (`app.py`) is not yet connected.

**Data model.** `Owner` aggregates `Pet`s, and each `Pet` aggregates its own `Task`s (`Owner → Pet → Task`). `Task` carries `duration`, a `Priority` (`IntEnum`), `frequency` (`once`/`daily`/`weekly`), an optional `fixed_time`, and an optional `due_date`. `Task.is_due(day)` returns true for incomplete tasks whose due date has arrived. `Task.mark_complete()` returns the next occurrence for recurring tasks, and `Pet.complete_task()` appends it to the pet's list. `Task` uses identity equality (`eq=False`), so two tasks with the same title remain distinct.

**Scheduling.** `Scheduler` reads from `Owner.get_all_tasks()` rather than any single pet, so tasks from every pet compete for the same time budget. `generate_plan(day)` filters to due tasks, sorts them by priority (shorter first within a priority), and builds a `Plan` in three steps:

1. Fixed-time tasks are placed first. Overlaps are detected with an interval check (`a.start < b.end and b.start < a.end`), and the lower-priority task in a conflict is skipped.
2. Remaining flexible tasks are fitted greedily against the minutes left after the fixed tasks (`available_minutes` minus fixed durations). A task that doesn't fit is skipped, and shorter tasks after it are still considered.
3. Each flexible task is placed in the earliest free gap at or after `Owner.day_start`.

Unscheduled tasks are recorded as `SkippedTask`s with a reason string. `main.py` and the Streamlit app format their output directly from `plan.items` and `plan.skipped`.

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

### UI features

Run the app with `streamlit run app.py`. In the browser a user can:

- **Set up the owner.** Enter a name and the minutes available today.
- **Add pets.** Enter a name and choose dog, cat or other. Duplicate pet names are rejected with an error message.
- **Add tasks.** Pick a pet, then set the title, duration, priority and frequency (once, daily or weekly). Optionally tick **Fixed time** to give the task a start time.
- **Review tasks.** The task table can be sorted by time and filtered by pet and by status (all, pending or completed).
- **Complete tasks.** Marking a daily or weekly task complete shows the date of its next occurrence.
- **Generate a schedule.** The schedule table shows each task's time and the reason it was placed there. It also shows tasks scheduled, minutes used and tasks skipped, with a warning and reason for each skipped task.

### Example workflow

1. Add a pet, for example "Mochi" (dog).
2. Add a task: "Morning walk", 30 minutes, high priority, daily, fixed time 07:30.
3. Add a second task: "Vet call", 30 minutes, medium priority, fixed time 07:45.
4. A warning appears above the task list because the two tasks overlap, naming both and the time windows.
5. Click **Generate schedule**. "Morning walk" is scheduled, and "Vet call" is listed as skipped because it overlaps the higher-priority task.
6. Under **Mark a task complete**, complete "Morning walk". The app confirms that the next occurrence is scheduled for tomorrow.

### Scheduler behaviors shown

- **Sorting.** The task table orders tasks by fixed time (`Scheduler.sort_by_time`), with flexible tasks last.
- **Filtering.** The pet and status filters use `Scheduler.filter_tasks`, alone or combined.
- **Conflict warnings.** Overlapping fixed-time tasks are reported without crashing, for the same pet or across pets (`Scheduler.conflict_warnings`).
- **Conflict resolution.** The higher-priority task keeps its slot and the other is skipped with a reason (`Scheduler.generate_plan`).
- **Recurrence.** Completing a daily or weekly task creates the next occurrence (`Scheduler.complete_task`).

### Sample CLI output

Output from `python main.py`, which builds the tasks out of time order, prints the schedule, then shows the sorted and filtered views and a conflict check:

```
Today's Schedule for John (Tuesday, October 20, 2026)
==================================================
07:30 - 08:00  Morning walk (Bingo, high priority)
08:00 - 08:20  Brush coat (Bingo, low priority)
09:00 - 09:15  Play with feather toy (Valentine, low priority)
12:15 - 12:30  Litter box cleaning (Valentine, medium priority)
18:00 - 18:10  Evening feeding (Bingo, high priority)

Added order (unsorted)
--------------------------------------------------
   18:00  Evening feeding (Bingo, pending)
flexible  Brush coat (Bingo, pending)
   07:30  Morning walk (Bingo, pending)
   12:15  Litter box cleaning (Valentine, done)
   09:00  Play with feather toy (Valentine, pending)
   12:15  Litter box cleaning (Valentine, pending)

Sorted by time
--------------------------------------------------
   07:30  Morning walk (Bingo, pending)
   09:00  Play with feather toy (Valentine, pending)
   12:15  Litter box cleaning (Valentine, done)
   12:15  Litter box cleaning (Valentine, pending)
   18:00  Evening feeding (Bingo, pending)
flexible  Brush coat (Bingo, pending)

Pending only
--------------------------------------------------
   18:00  Evening feeding (Bingo, pending)
flexible  Brush coat (Bingo, pending)
   07:30  Morning walk (Bingo, pending)
   09:00  Play with feather toy (Valentine, pending)
   12:15  Litter box cleaning (Valentine, pending)

Completed only
--------------------------------------------------
   12:15  Litter box cleaning (Valentine, done)

Bingo's tasks
--------------------------------------------------
   18:00  Evening feeding (Bingo, pending)
flexible  Brush coat (Bingo, pending)
   07:30  Morning walk (Bingo, pending)

Valentine's pending tasks, by time
--------------------------------------------------
   09:00  Play with feather toy (Valentine, pending)
   12:15  Litter box cleaning (Valentine, pending)

Conflict check
--------------------------------------------------
Warning: 'Morning walk' 07:30-08:00 overlaps 'Vet check-in' 07:30-08:00 - same pet (Bingo)
Warning: 'Evening feeding' 18:00-18:10 overlaps 'Grooming' 18:00-18:30 - different pets (Bingo and Valentine)
Today's Schedule for John (Tuesday, October 20, 2026)
==================================================
07:30 - 08:00  Morning walk (Bingo, high priority)
08:00 - 08:20  Brush coat (Bingo, low priority)
09:00 - 09:15  Play with feather toy (Valentine, low priority)
12:15 - 12:30  Litter box cleaning (Valentine, medium priority)
18:00 - 18:10  Evening feeding (Bingo, high priority)
```
