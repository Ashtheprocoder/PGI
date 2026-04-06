Design System Conventions
Follow these design system conventions for all UI work in this project.
Spacing Scale
Use a consistent spacing scale. Never use arbitrary pixel values.

4px — tight spacing (icon gaps, inline padding)
8px — default element spacing
12px — compact section spacing
16px — standard content padding
24px — section spacing
32px — large section gaps
48px — page-level spacing
64px — major layout divisions

Color Tokens
Use semantic color names, not raw hex values:






 
 
--color-text-primary
— main body text
--color-text-secondary
— supporting/muted text --color-text-tertiary
— timestamps, labels, hints
--color-surface
 — page/card background --color-surface-raised
— elevated cards, modals






 
 
--color-border
— default borders
--color-border-subtle
 — light dividers --color-accent
— primary actions, links
--color-accent-hover
— hover state for accent --color-success
, --color-warning
, --color-error
— status colors
Define tokens as CSS custom properties. Support both light and dark themes by
swapping token values, not changing component styles.
Typography

Use a type scale with clear hierarchy: display, heading, subheading, body, caption,
overline
Limit to 2 font families max (one for headings, one for body — or just one for
everything)
Set line-height relative to font size: headings at 1.2–1.3, body at 1.5–1.6
Use font-weight to create hierarchy: 400 for body, 500 for emphasis, 600–700 for
headings
Cap line length at 65–75 characters for readability

Component Patterns

Border radius: Pick one value and use it consistently (e.g., 8px for cards, 6px
for inputs, 4px for small elements)
Shadows: Use a 3-level elevation system (sm, md, lg) instead of custom shadows
everywhere
Transitions: Default to 150ms ease-out for micro-interactions, 250ms for layout
changes
States: Every interactive element needs default, hover, active, focus, and
disabled states
Icons: Use one icon set consistently. Match icon size to text size (16px icons
with 14–16px text)

Layout

Use a max-width container for content (e.g., 1200px for full layouts, 720px for
text-heavy pages)
Use CSS Grid for page layouts, Flexbox for component-level alignment
Keep consistent gutter widths (16px on mobile, 24px on tablet, 32px on desktop)
Align elements to the spacing scale — if something looks off, it's probably not on
the grid