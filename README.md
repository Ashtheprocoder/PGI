# PGI — Personal Growth Index Dashboard

PGI is a lightweight personal growth dashboard that combines:

- **Habit data** from TheFor JSON export (`habits-*.json`)
- **Historical PGI baseline** from Excel (`PGI_v3.xlsx`, optional)
- **Task completion data** from Todoist (optional via `TODOIST_TOKEN`)

The goal is a reliable, easy-to-refresh personal score and habit tracking system with minimal setup.

## What this repo contains

- `refresh_dashboard.py` — main data pipeline and static page generator
- `PGI_Dashboard.html` — generated main dashboard page
- `habit_detail.html` — generated habit detail page
- `data/latest.json` — persisted fallback payload and latest generated data
- `docs/roadmap.md` — product source of truth and MVP priorities
- `scripts/smoke_test.sh` — repeatable smoke checks
- `tests/test_refresh_smoke.py` — parser/fallback smoke tests

## Quick start

### 1) Requirements

- Python 3.10+
- Optional for Excel history merge:
  - `pandas`
  - `openpyxl`

Install dependencies:

```bash
python3 -m pip install pandas openpyxl
```

### 2) Add data files

Put these in the repo root:

- TheFor export named like `habits-6-4-2026.json`
- Optional historical workbook: `PGI_v3.xlsx`

### 3) (Optional) Todoist token

```bash
export TODOIST_TOKEN="your_token_here"
```

### 4) Regenerate dashboard

```bash
python3 refresh_dashboard.py
```

This regenerates:

- `PGI_Dashboard.html`
- `habit_detail.html`
- `data/latest.json`

<<<<<<< ours
<<<<<<< ours
=======
=======
>>>>>>> theirs
## Unified MVP payload (new)

`data/latest.json` now includes an `mvp` object (backward-compatible additive field) for the first MVP dashboard slices:

- `sync_status`
- `tasks_overview`
- `projects_overview`
- `deadline_visibility`
- `current_focus`
- `growth_score`
- `weekly_review`

<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
## Data flow and scoring

1. Script finds latest `habits-*.json` export.
2. Habit export is parsed and normalized using alias mapping.
3. If enabled and available, Excel rows before TheFor start date are merged.
4. If Todoist token is present, completed tasks are fetched and scored.
5. Daily, weekly, monthly aggregates and streaks are computed.
6. Static HTML pages + `data/latest.json` are written.

### Scoring basics

- Habit day score = configured habit points for completed habits, `-1` for missed habits.
- Todoist task points are added by completion timing:
  - on-time: `+2`
  - overdue: `+1`
  - no due date: `+1`

## Reliability features

- Run lock file (`.refresh_dashboard.lock`) prevents concurrent refresh corruption.
- Atomic write for `data/latest.json`.
- Fallback behavior: if TheFor export is missing/invalid, script can load `data/latest.json`.
- Parser supports both list-shaped and dict-shaped TheFor payloads.

## Smoke testing

Run this anytime before commit:

```bash
scripts/smoke_test.sh
```

Checks include:

- unit smoke tests
- `.DS_Store` not tracked
- required docs/skills paths present
- `refresh_dashboard.py` compiles

## GitHub Pages publishing

### Why `index.html` is needed

GitHub Pages serves `index.html` at repo root for project URLs.
If your dashboard file is `PGI_Dashboard.html`, add a small redirect `index.html`:

```html
<!doctype html>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=./PGI_Dashboard.html">
<title>Redirecting…</title>
<a href="./PGI_Dashboard.html">Open PGI Dashboard</a>
```

### Pages settings

Repo Settings → Pages:

- Source: **Deploy from a branch**
- Branch: `main`
- Folder: `/(root)`

Project URL format:

```text
https://<username>.github.io/<repo>/
```

## Troubleshooting

### PGI starts from 2025-05-01 only (missing older history)

Cause: Excel merge was skipped.

Fix:

1. Install deps: `python3 -m pip install pandas openpyxl`
2. Re-run: `python3 refresh_dashboard.py`
3. Confirm logs show non-zero Excel rows.

### `git push` rejected (fetch first)

You are behind remote. Use:

```bash
git pull --rebase origin main
git push origin main
```

If dirty working tree blocks rebase:

```bash
git add .
git commit -m "WIP"
git pull --rebase origin main
```

### zsh `event not found: doctype`

You pasted HTML directly into shell. Use `cat <<'EOF'` heredoc to create files.

## Why `docs/PGI_technical_roadmap.md` might be missing

That file can exist locally on a branch but not on `main` if it was never committed/pushed (or got dropped during reset/rebase conflict cleanup).

To restore from another local branch:

```bash
git checkout main
git checkout <branch-with-file> -- docs/PGI_technical_roadmap.md
git add docs/PGI_technical_roadmap.md
git commit -m "Add PGI technical roadmap"
git push origin main
```

## Roadmap source of truth

Use `docs/roadmap.md` as product source of truth for stabilization and MVP sequencing.

---

If you want, next step is to add a tiny CLI command wrapper (`make refresh`, `make smoke`) to reduce command friction.
