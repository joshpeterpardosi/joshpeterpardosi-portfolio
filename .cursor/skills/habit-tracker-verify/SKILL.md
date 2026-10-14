---
name: habit-tracker-verify
description: Run and verify the habit-tracker server in habit-tracker/ against a real running process (duplicate check-in, streak reset, persistence). Use when changing habit-tracker code or adding test cases.
---

# Habit tracker verification

## Run the server
```bash
cd habit-tracker
HABIT_DATA_FILE=/tmp/habits.json HABIT_TODAY=2026-10-05 python3 src/server.py 8000
curl -X POST localhost:8000/habits -d '{"name":"Read"}'
curl -X POST localhost:8000/habits/<id>/check-in
curl localhost:8000/habits/<id>/streak
```
`HABIT_TODAY` is optional (defaults to the real date). Data model: `habit_id`, `name`, `created_at`, `check_ins` only. Streak = consecutive days ending today or yesterday, 0 otherwise; computed per request, never stored.

## Run the harness
```bash
cd habit-tracker && python3 -m unittest discover -s tests -v
```
No dependencies. Each test spawns `src/server.py` as a subprocess on a free port with a temp data file and talks real HTTP.

## What each assertion proves
- `test_duplicate_check_in_same_day_rejected`: second same-day check-in returns 409 and `check_ins` is unchanged both via API and on disk.
- `test_streak_resets_after_missed_day`: with `fixtures/streak_cases.json` and today=2026-10-05: a gap resets (1), unbroken run counts (5), run ending yesterday still counts (3), last check-in older than yesterday gives 0.
- `test_missed_day_live_reset`: same rule produced through real check-ins over several server processes with different `HABIT_TODAY`.
- `test_data_persists_across_restart`: create + check-in, SIGKILL the process, new process (different PID) on the same file returns the same check-ins and streak; dedupe still holds; stored record has exactly the four fields.

## Add a case
1. Streak case: add a habit to `fixtures/streak_cases.json` (or a new fixture file) and its expected streak to the `expected` dict, or copy the new fixture in a new test.
2. Behavior case: add a `test_*` method using `self.start(today)` and `server.call(method, path, body)`. Assert against HTTP responses and/or the data file, never internal functions.
3. To reproduce a bug: write the failing test first, see it fail, then fix.
