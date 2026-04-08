# PGI Roadmap (Source of Truth)

_Last updated: 2026-04-08_

## Product goal
Build a personal gamified growth system that adapts to current goals, projects, and objectives, and improves clarity + motivation.

## Stability-first rules
1. Fix repo and data reliability issues before adding features.
2. Keep changes minimal and backward-compatible.
3. Favor clarity/reliability over polish.
4. Delay advanced gamification until core sync + dashboard flow is stable.

## MVP priorities (ordered)
1. Unified data model (habits + tasks + derived metrics)
2. Reliable sync/import layer
   - TheFor JSON import
   - Todoist task sync
3. Dashboard home page
4. Habit progress
5. Task/project overview
6. Deadline visibility
7. Current focus
8. Simple growth score
9. Weekly review summary

## Current stabilization checklist
- [ ] remove `.DS_Store` from tracked files
- [ ] check repo alignment / clone consistency
- [ ] harden `refresh_dashboard.py`
- [ ] verify lock file protection
- [ ] verify `data/latest.json` fallback behavior
- [ ] confirm skills + docs structure consistency
- [ ] add at least one repeatable smoke test

## Next implementation phase after stabilization
- Build a minimal unified `data/latest.json` contract consumed by dashboard pages.
- Keep rendering logic simple and deterministic.
- Add focused tests for parser + aggregation regressions.
