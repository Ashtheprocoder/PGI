---
name: accessibility
description: "Teach Claude to build accessible interfaces by default. Drop this file into your project root so Claude uses semantic HTML, proper contrast, focus management, ARIA attributes, and keyboard navigation in everything it builds."
---
 
# Accessibility Conventions
Follow these accessibility practices for all UI work in this project. Accessibility
is not optional — build it in from the start.
## Semantic HTML
- Use the correct HTML element for its purpose:
`<button>` for actions,
navigation,
`<input>` for data entry
- Never use
`<div>`
or
`<span>` for interactive elements
- Use heading levels (`<h1>` through `<h6>`) in order — don't skip levels
- Use
`<nav>`
,
`<main>`
,
`<aside>`
,
`<header>`
,
`<footer>`
,
`<section>`
,
for page landmarks
- Use
`<ul>`/`<ol>` for lists of items,
`<table>` for tabular data
- Use
`<label>` for every form input, with explicit `for
`/`id`
association
`<a>` for
`<article>`
## Color & Contrast
- Text must meet WCAG AA contrast ratios: 4.5:1 for normal text, 3:1 for large text
(18px+ or 14px+ bold)
- Never use color as the only way to convey information (add icons, text, or
patterns)
- UI components and graphical objects need 3:1 contrast against adjacent colors
- Test both light and dark themes for contrast compliance
- Provide sufficient contrast for placeholder text (use it sparingly — labels are
better)
## Focus Management
- Every interactive element must have a visible focus indicator
- Focus indicators should have at least 3:1 contrast and be clearly distinguishable
`
- Use
outline
` for focus styles, not just `border
`
or
`box-shadow
` (outlines don't
affect layout)
- Manage focus when content changes: move focus to new modals, return focus when they
close
- Use
`tabindex="0"` to make custom elements focusable,
`tabindex="
-1"` for
programmatic focus only
- Never use
`tabindex
`
values greater than 0
## Keyboard Navigation
- All functionality must be operable with keyboard alone
- Use standard keyboard patterns: Tab to move between elements, Enter/Space to
activate, Escape to dismiss
- Arrow keys for navigating within components (tabs, menus, radio groups)
- Don't trap keyboard focus — users must always be able to Tab away from any
component
- Provide skip links ("Skip to main content") at the top of the page
## ARIA
- Use ARIA only when semantic HTML isn't sufficient — prefer native elements first
- Required ARIA for common patterns:
- Modals:
`
role="dialog"`
,
`
aria-modal="true"`
`
,
aria-labelledby
`
- Tabs:
`
role="tablist"`
`
,
role="tab"`
`
,
role="tabpanel"`
`
,
aria-selected`
- Alerts:
`
role="alert"`
`
or
aria-live="polite"` for status messages
- Toggles:
`
aria-pressed`
`
or
aria-expanded`
- Loading states:
`
aria-busy="true"`
, announce with live region
- Always provide
`
aria-label`
`
or
aria-labelledby
` for elements without visible text
labels
- Use
`
aria-describedby
` for supplementary descriptions (error messages, help text)
`
- Use
aria-hidden="true"` for decorative elements (icons next to text labels)
## Images & Media
- Every
`<img>`
needs an
`
alt`
attribute — descriptive for meaningful images, empty
(`
alt=""`) for decorative
- Complex images (charts, diagrams) need longer descriptions via
`
or a text alternative
- Video needs captions, audio needs transcripts
- Avoid auto-playing media — if unavoidable, provide pause/stop controls
aria-describedby
`
## Motion & Animation
- Respect `
prefers-reduced-motion
`
— disable or reduce animations when this is set
- Never rely on animation to convey essential information
- Avoid flashing content (nothing flashing more than 3 times per second)
## Forms
- Every input needs a visible label (not just placeholder text)
- Group related inputs with `<fieldset>`
and `<legend>`
- Mark required fields with both visual indicator and `
aria-required="true"`
- Display error messages near the input, associated with `
aria-describedby
`
`
- Use
aria-invalid="true"` for fields with errors
- Announce form submission results to screen readers with live regions