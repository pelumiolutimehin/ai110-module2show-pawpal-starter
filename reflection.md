# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - The design supports three core user actions: add a pet, add care tasks (such as a walk) for that pet, and view a daily plan for the pet(s). The owner's available time and preferences are the constraints that shape the plan.
  - Data flows in one direction: an `Owner` has `Pet`s, each `Pet` has `Task`s, and a `Scheduler` reads the owner's data and produces a `Plan`. The scheduling logic is kept separate from the data classes so it can be tested without the Streamlit UI.
- What classes did you include, and what responsibilities did you assign to each?
  - **Owner**: holds the owner's name, `available_minutes` for the day, `preferences`, and their list of pets. It is the entry point for the data and supplies the time constraint the scheduler uses.
  - **Pet**: holds the pet's name, species, breed, and its `tasks_list`. It adds and removes tasks and can report which tasks are still pending.
  - **Task**: represents one care activity, with a title, duration, priority, category, frequency, an optional `fixed_time`, and a completed flag. It knows whether it is due on a given day and can mark itself complete, creating the next occurrence if it recurs.
  - **Scheduler**: the "brain" of the app. It holds the owner, sorts tasks by priority, fits them into the available time, detects conflicts between fixed-time tasks, and returns a `Plan`.
  - **Plan**: the result of scheduling. It holds the scheduled items, the skipped tasks, and the total minutes, and can explain the plan in plain text.
  - **ScheduledItem**: one task placed in the plan, with a start time, end time, and the reason it was placed there.
  - **SkippedTask**: a task left out of the plan, with the reason (for example, not enough time).


**b. Design changes**

- Did your design change during implementation? Yes ✅
- If yes, describe at least one change and why you made it.
  - Added a pet_name attribute to the Task class: Task.pet_name is set by Pet.add_task, so that plans can say which pet a task is for and users can filter by pet

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - It considers the owner's available minutes, each task's priority, optional fixed start times, and due dates and frequency. Tasks are only scheduled if they're incomplete and due. Owner preferences are stored but not used yet.
- How did you decide which constraints mattered most?
  - Fixed times come first because they can't move, such as a medication at a set hour. Priority comes next so the most important care survives when time runs short. The time budget decides what gets skipped, and every skipped task is listed with a reason.
    
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - When two fixed-time tasks overlap, `generate_plan` keeps the higher-priority one and skips the other, listing it in the plan with the reason. It does not try to move the skipped task to a free slot. Priority order is a simple greedy rule, with shorter tasks first within a priority.
- Why is that tradeoff reasonable for this scenario?
  - A pet owner's day has only a handful of tasks, so a rule they can predict and read matters more than an optimal plan. "The higher-priority task wins" is easy to explain and test, and every skipped task is listed with a reason. The cost is that a low-priority task, such as grooming, is dropped when it could have been moved 30 minutes later, so automatic rescheduling is the first thing I would add next.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - I used Claude for design brainstorming, fleshing out the skeleton code for the classes, and the composing the full implementation for the classes.
- What kinds of prompts or questions were most helpful?
  - Mainly questions about how to go about designing this application were most helpful. Since I haven't really used or worked with this kind of application, the extra help was important.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - One moment where I didn't accept an AI suggestion was when Task.mark_complete() was implemented, Claude computed the next due date as (due_date or today) + interval. I questioned this because it seemed to make recurrence relative to the completion date instead of a fixed schedule. Claude's code actually used due_date as the anchor when one was set. But the mix of two behaviors was a real flaw, so I had it switch to a consistent fixed schedule that never lands in the past, and document the rule in the docstring and README.
- How did you evaluate or verify what the AI suggested?
  - I evaluate the AI's suggestion by reading through the somewhat complex logic implementations line-by-line to ensure there were no gaps.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - I wrote 26 tests covering four areas: sorting by time (chronological order, midnight, flexible tasks last, tie-breaks), filtering by pet and completion status, conflict warnings (same pet, different pets, back-to-back, completed tasks), and recurrence (daily and weekly next dates, month, year and leap-year rollovers, late completion, no duplicates).
- Why were these tests important?
  - These behaviors are the ones an owner would notice if they broke, such as a missed warning, a recurring task that never comes back, or one that comes back twice. Several tests also protect edge cases that were easy to get wrong, like a 9:00 task sorting before a 10:00 one.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - Quite confident (5 out of 5 stars) in the scheduler's core behavior: sorting, filtering, conflict warnings, recurrence and generate_plan all have direct tests that pass. The remaining risk is the known limitations below, not untested logic.
- What edge cases would you test next if you had more time?
  - First, `generate_plan` directly: a clash between a high- and a low-priority task, a plan that runs out of time, and a flexible task placed around a fixed one. After that, a task that runs past midnight, weekly rollovers, and a plan with no tasks at all.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I'm most satisfied with the recurrence logic and keeping the scheduling code separate from the UI. Recurring tasks follow a fixed schedule that never lands in the past and can't be duplicated, and tests cover the date edge cases. Because the logic is separate, I could test it and demo it from the command line before touching Streamlit.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - Next I would add direct tests for `generate_plan`, since it has only been checked by running `main.py`. I would also add task editing and removal in the UI, because the conflict warning asks users to change a start time but they currently can't. Finally, I would make the scheduler use `Owner.preferences`, which is stored today but never read.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - The most important thing I learned is that AI is a fast collaborator but not a replacement for my own judgment. It wrote working code quickly, but a mixed recurrence rule only got fixed because I questioned it and read the logic line by line. Designing the classes first and keeping the logic separate from the UI also made everything easier to test and change.

---

## 6. AI Strategy

**a. Most effective features**

- Which AI coding assistant features were most effective for building your scheduler?
  - Three features helped most. Design brainstorming helped me weigh algorithms and tradeoffs before writing code. Letting the assistant edit files and run `main.py` and `pytest` showed me right away whether a change worked. Test generation covered edge cases, like month and leap-year rollovers, that I might not have thought of.

**b. Rejecting or modifying a suggestion**

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
  - The first `Task.mark_complete()` computed the next due date two different ways, depending on whether a due date was set. I had it switch to one rule: the next due date is the previous due date plus the interval, and never in the past. That kept recurrence logic in one place, with `Pet.complete_task` simply adding whatever `mark_complete` returns.

**c. Separate chat sessions**

- How did using separate chat sessions for different phases help you stay organized?
  - I used a separate session for each phase: design, implementation, and then tests, UI and documentation. Each session started with only the context that phase needed, so the assistant wasn't distracted by earlier decisions and its answers stayed focused. It also made it easier to find where I had made a decision.

**d. Being the lead architect**

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
  - Being the lead architect meant I decided what the system should do and how its parts fit together, and the AI helped build it. I set the class structure, the tradeoffs (like skipping a conflicting task instead of rescheduling it), and the rules, such as the fixed recurrence schedule. Then I checked everything the AI produced by reading the logic and running the tests, because it can sound confident and still be wrong. The best results came when I gave clear direction and verified the output, not when I accepted whatever it wrote.
