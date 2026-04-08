# PGI MVP Execution Plan

_Last updated: 2026-04-08_

This document is the implementation plan for finishing the PGI MVP while keeping `main` stable.

## Working model

- `main` = stable/live branch
- `feat/mvp-unified-data-model` = active MVP development branch

## MVP definition of done

MVP is complete when all of the following are true:

1. Unified payload exists and is backward-compatible in `data/latest.json`.
2. TheFor sync/import is reliable.
3. Todoist sync/import is reliable or fails gracefully.
4. Dashboard home shows:
   - task/project overview
   - deadline visibility
   - current focus
   - weekly review
   - simple growth score
5. Habit detail view still works.
6. Smoke tests pass and no conflict markers remain.
7. GitHub Pages deploy is healthy.

## Phase plan

### Phase 0 — Stabilization lock (done)
- Keep lock/fallback protections in refresh pipeline.
- Keep smoke checks green.

### Phase 1 — Data contract (in progress)
- Finalize `mvp` block structure in payload.
- Add explicit version field and sync status details.
- Ensure additive schema only (no breaking changes).

### Phase 2 — Home dashboard MVP sections
- Render `mvp.tasks_overview`.
- Render `mvp.deadline_visibility`.
- Render `mvp.current_focus`.
- Render `mvp.weekly_review` + `mvp.growth_score`.
- Keep UI minimal and readable.

### Phase 3 — Reliability and regressions
- Add tests for `mvp` payload shape and edge cases.
- Validate behavior with:
  - Excel present + absent
  - Todoist token present + absent
  - empty/partial data

### Phase 4 — Merge readiness
- Complete merge checklist.
- Merge feature branch to `main`.
- Tag pre/post merge release points.

## Merge readiness checklist

Run and verify all before merge:

```bash
scripts/smoke_test.sh
python3 refresh_dashboard.py
grep -nE '^<<<<<<< .*$|^=======$|^>>>>>>> .*$' refresh_dashboard.py tests/test_refresh_smoke.py PGI_Dashboard.html habit_detail.html data/latest.json
```

Manual checks:

- Open `PGI_Dashboard.html` and verify MVP sections render.
- Open `habit_detail.html` and verify no regressions.
- Validate generated values in `data/latest.json`.

## Safe commit discipline

- Commit in small chunks by feature.
- Use clear commit messages (`MVP step: ...`).
- Push often to feature branch.
- Do not merge to `main` until checklist is complete.

## Rollback strategy

Before merge to `main`:

```bash
git checkout main
git pull origin main
git tag -a pre-mvp-merge-YYYYMMDD -m "pre-mvp merge backup"
git push origin pre-mvp-merge-YYYYMMDD
```

Emergency rollback:

```bash
git checkout main
git reset --hard pre-mvp-merge-YYYYMMDD
git push --force-with-lease origin main
```
