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
- How did you decide which constraints mattered most?

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
  - One where I didn't accept an AI suggestion was when Task.mark_complete() was implemented, Claude computed the next due date as (due_date or today) + interval. I questioned this because it seemed to make recurrence relative to the completion date instead of a fixed schedule. Claude's code actually used due_date as the anchor when one was set. But the mix of two behaviors was a real flaw, so I had it switch to a consistent fixed schedule that never lands in the past, and document the rule in the docstring and README.
- How did you evaluate or verify what the AI suggested?
  - I evaluate the AI's suggestion by reading through the somewhat complex logic implementations line-by-line to ensure there were no gaps.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
