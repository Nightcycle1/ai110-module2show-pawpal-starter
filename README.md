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

PawPal+ is an intelligent pet care scheduling assistant that helps busy pet owners manage their pets' daily care tasks. It automatically generates optimized schedules based on task priorities, owner availability, and time constraints while providing clear explanations for every scheduling decision.

## 📸 Demo

<a href="/images/pawpal_demo.png" target="_blank">
  <img src="/images/pawpal_demo.png" alt="PawPal+ App Screenshot" width="100%"/>
</a>

*Screenshot of PawPal+ generating a daily schedule with conflict detection and reasoning*

## ✨ Features

### 🎯 Smart Scheduling
- **Priority-Based Planning**: Tasks are scheduled by priority (High > Medium > Low), ensuring critical tasks get precedence
- **Fixed & Flexible Tasks**: Handles both time-sensitive tasks (e.g., medication at 8am) and flexible activities (e.g., walks, playtime)
- **Automatic Time Slot Finding**: Uses 30-minute granularity to find optimal time slots within owner's available hours

### 🔄 Recurring Tasks
- **Daily Recurrence**: Perfect for feeding, walks, or daily medications
- **Weekly Recurrence**: Ideal for vet visits, grooming, or weekly cleaning
- **Automatic Next Occurrence**: Completed recurring tasks automatically generate their next occurrence

### ⚡ Conflict Detection
- **Fixed-Time Conflicts**: Detects overlapping fixed-time tasks
- **Cross-Pet Conflicts**: Identifies scheduling conflicts when managing multiple pets
- **Time Feasibility**: Warns when total task time exceeds available hours

### 📊 Rich UI Experience
- **Interactive Task Management**: Add, edit, and delete tasks with all attributes
- **Visual Schedule Display**: Color-coded schedule (🔴 High, 🟡 Medium, 🟢 Low priority)
- **Detailed Reasoning**: Every scheduling decision includes human-readable explanations
- **Conflict Preview**: Check for conflicts before generating the full schedule

### 🧪 Comprehensive Testing
- 9 core tests covering sorting, recurrence, and conflict detection
- Edge case validation for one-off tasks and duplicate times
- Integration tests for multi-pet conflict detection


## Testing PawPal+

Run the test suite to verify scheduling logic:

```bash
python -m pytest

