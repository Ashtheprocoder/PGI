---
name: dark-mode
description: "Teach Claude to build proper light/dark mode support from the start — not as an afterthought. Drop this file into your project root so Claude uses semantic color tokens, respects system preferences, and handles the tricky edge cases (images, shadows, borders) that make dark mode feel polished."
---
 
# Dark Mode Conventions
Follow these dark mode conventions for all UI work in this project. Dark mode is not
an inversion filter — it requires intentional color decisions.
## Color Token Architecture
Define all colors as semantic tokens. Never use raw hex/rgb values in components.
```
css
:root {
/* Surfaces */
--color-bg-primary: #ffffff;
--color-bg-secondary: #f5f5f7;
--color-bg-tertiary: #e8e8ed;
--color-bg-elevated: #ffffff;
/* Text */
--color-text-primary: #1d1d1f;
--color-text-secondary: #6e6e73;
--color-text-tertiary: #aeaeb2;
/* Borders */
--color-border: #d2d2d7;
--color-border-subtle: #e8e8ed;
/* Interactive */
--color-accent: #0071e3;
--color-accent-hover: #0077ed;
}
[data-theme="dark"] {
/* Surfaces — NOT inverted white. Use dark grays.
*/
--color-bg-primary: #1c1c1e;
--color-bg-secondary: #2c2c2e;
--color-bg-tertiary: #3a3a3c;
--color-bg-elevated: #2c2c2e;
/* Text — slightly off-white to reduce eye strain */
--color-text-primary: #f5f5f7;
--color-text-secondary: #a1a1a6;
--color-text-tertiary: #6e6e73;
/* Borders — subtle in dark mode */
--color-border: #3a3a3c;
--color-border-subtle: #2c2c2e;
/* Interactive — slightly brighter in dark mode for visibility */
--color-accent: #0a84ff;
--color-accent-hover: #409cff;
}
```
## System Preference Detection
Always respect the user's system preference as the default:
```
css
@media (prefers-color-scheme: dark) {
:root:not([data-theme="light"]) {
/* dark token values */
}
}
```
Allow manual override that persists across sessions. Store the choice in
`localStorage
`
. Three states: system (default), light, dark.
## Surfaces & Elevation
- Dark mode is NOT pure black (`#000000`) — use dark grays (`#1c1c1e
`) for the base
- Create depth through slightly lighter grays, not shadows
- Elevated surfaces (modals, cards, dropdowns) should be lighter than the base, not
darker
- Reduce shadow intensity in dark mode — shadows are nearly invisible on dark
backgrounds
- Use subtle borders instead of shadows to define edges in dark mode
## Text & Contrast
- Primary text should be off-white (`#f5f5f7`), not pure white (`#ffffff`) — reduces
eye strain
- Maintain WCAG AA contrast ratios in both modes (4.5:1 for body text)
- Secondary text needs more contrast adjustment than primary — test carefully
- Colored text (links, status) may need different shades in dark mode to maintain
readability
## Images & Media
- Use
`filter: brightness(0.9)`
on user-uploaded images in dark mode to reduce glare
- Provide dark variants of logos and illustrations when possible
- SVG icons should use
`
currentColor
`
so they adapt automatically
- Screenshots and diagrams with white backgrounds look jarring — add a subtle border
or rounded container
- Avoid transparent PNGs that assume a light background
## Borders & Dividers
- Borders that work in light mode often disappear in dark mode — test both
`
- Use
--color-border
` tokens instead of hardcoded values
- Consider using
`
rgba()` borders that adapt:
`
rgba(255, 255, 255, 0.1)` in dark,
`
rgba(0, 0, 0, 0.1)` in light
- Dividers should be more subtle in dark mode, not more prominent
## Form Inputs
- Input backgrounds should be slightly different from the page background in both
modes
- Focus rings need to be visible in both modes — blue works well in both
- Placeholder text contrast is tricky in dark mode — test it
- Disabled states need to be distinguishable in both modes
## Transitions
- When switching themes, transition
`background-color
`
and `
color
`
with `150ms ease
`
- Apply transition to
`body
`
or
`
:root`
, not individual elements (avoids flash of
unstyled content)
- Don't transition images or media — only colors
## Testing
- Always test both modes during development, not just at the end
- Check all states: hover, focus, active, disabled, error, loading
- Test with actual content, not just placeholder text
- Verify no hardcoded colors leak through in either mode