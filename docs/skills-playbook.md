# Skills Playbook

## Should I copy/paste skills from Claude?
Short answer: **No** — use Claude output as raw input, then adapt it.

## Where to add skills
- Per our agreement, store skills **inside this git repo** under: `skills/<skill-name>/SKILL.md`
- Keep optional helpers next to that file:
  - `skills/<skill-name>/scripts/`
  - `skills/<skill-name>/assets/`
  - `skills/<skill-name>/references/` (only if needed)
- **This `SKILLS_PLAYBOOK.md` is guidance only** — do not paste full skill bodies here.
- Add a short `README.md` in `skills/` (or per-skill folders) when conventions change.

## Minimal skill folder example
```text
skills/
  trading-review/
    SKILL.md
    scripts/
      generate_report.py
    assets/
      template.md
```
## README vs SKILL.md
- **Put the actual skill content in** `skills/<skill-name>/SKILL.md`.
- **Do not paste full skill instructions into** `README.md`.
- Use `README.md` only for navigation, conventions, and links to the real `SKILL.md` files.

## Recommended workflow
1. **Start from your local skill format**
   - Keep expected structure (`SKILL.md`, optional `scripts/`, optional `assets/`).
2. **Translate, don't transplant**
   - Rewrite instructions so they match your tools, file paths, and naming.
3. **Verify every command and path**
   - Run commands locally and fix assumptions before publishing.
4. **Trim to smallest useful scope**
   - Keep the skill focused on one workflow; remove generic filler.
5. **Add guardrails**
   - Include failure modes, fallbacks, and "when not to use" guidance.
6. **Test with a real task**
   - Execute one realistic end-to-end example before considering the skill ready.

## Quality checklist before committing
- [ ] All referenced files/paths exist.
- [ ] Steps are actionable and deterministic.
- [ ] Tool usage is explicit (inputs/outputs clear).
- [ ] The skill works without relying on unstated context.
- [ ] The skill is concise and avoids duplicated instructions.
