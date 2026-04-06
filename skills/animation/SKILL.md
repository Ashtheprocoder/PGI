---
name: animation
description: "Teach Claude to use animation intentionally and tastefully. Drop this file into your project root so Claude applies sensible defaults for timing, easing, and motion — and respects users who prefer reduced motion."
---
 
# Animation Conventions
Follow these animation guidelines for all UI work in this project. Animation should
feel natural and purposeful — never gratuitous.
## Duration
Use these durations consistently. Faster for small elements, slower for larger
movements:
- **50–100ms** — Micro-interactions: button presses, toggle switches, checkboxes
- **150–200ms** — Small transitions: hover states, color changes, opacity fades
- **250–350ms** — Medium transitions: cards expanding, panels sliding, content
entering
- **400–500ms** — Large transitions: page transitions, modals appearing, full-screen
changes
Never exceed 500ms for UI animations. If it feels slow, it is slow.
## Easing
- **ease-out** (`
cubic-bezier(0.0, 0.0, 0.2, 1)`) — For elements entering the screen.
Starts fast, decelerates. Use this most of the time.
- **ease-in** (`
cubic-bezier(0.4, 0.0, 1, 1)`) — For elements leaving the screen.
Starts slow, accelerates out.
- **ease-in-out** (`
cubic-bezier(0.4, 0.0, 0.2, 1)`) — For elements that move from
one position to another on screen.
- **linear** — Only for continuous animations like loading spinners or progress bars.
Never use the CSS default `
ease
`
— it's generic and doesn't feel as natural.
## What to Animate
**Do animate:**
- Opacity changes (fading in/out)
- Transform (translate, scale, rotate)
- Background/border color changes on hover/focus
- Content entering and leaving the viewport
- State changes (expanded/collapsed, selected/unselected)
**Don't animate:**
- Layout properties (width, height, top, left, margin, padding) — causes reflows
- Initial page load content — it should just be there
- Decorative motion that doesn't communicate anything
- Multiple things at once competing for attention
## Entry/Exit Patterns
- **Fade in**:
`
opacity: 0 → 1`
- **Slide up**:
- **Scale in**:
, 200ms, ease-out
`translateY(16px) → translateY(0)` + fade, 250ms, ease-out
`
scale(0.95) → scale(1)` + fade, 200ms, ease-out
- **Slide out**: Reverse of entry, but faster (150–200ms), ease-in
Stagger sequential items by 50ms each (list items, cards). Don't stagger more than 5
items — after that, just show them.
## Reduced Motion
Always respect the user's motion preferences:
```
css
@media (prefers-reduced-motion: reduce) {
*
,
*::before,
*::after {
animation-duration: 0.01ms !important;
animation-iteration-count: 1 !important;
transition-duration: 0.01ms !important;
}
}
```
When reduced motion is enabled:
- Replace sliding/scaling with simple opacity fades
- Remove parallax effects entirely
- Keep essential state-change indicators (e.g., checkbox check mark) but make them
instant
- Auto-playing carousels should stop
## Performance
- Only animate
`
opacity
`
and `transform
`
— these are GPU-composited and don't trigger
layout/paint
`
- Use
will-change
`
sparingly and only on elements that will actually animate
`
- Remove
will-change
`
after animation completes for one-off animations
- Avoid animating during scroll — use
`IntersectionObserver
` to trigger animations
when elements enter the viewport
- Test animations at 60fps — if they stutter, simplify
## Interaction Feedback
- Buttons: subtle scale on press (`
scale(0.98)`), 100ms ease-out
- Cards: slight lift on hover (`translateY(-2px)` + shadow increase), 150ms ease-out
- Links: color transition, 150ms
- Toggles: slide + color change, 200ms ease-out
- Don't add hover effects on touch devices — use
`
:hover
`
within
`@media (hover:
hover)`