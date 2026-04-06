---
name: responsive
description: "Teach Claude to build layouts that work across every screen size. Drop this file into your project root so Claude uses mobile-first breakpoints, fluid layouts, proper touch targets, and responsive typography"
---
 
# Responsive Design Conventions
Follow these responsive design practices for all UI work in this project. Build
mobile-first — start with the smallest screen and scale up.
## Breakpoints
Use these standard breakpoints. Always write mobile styles first, then add min-width
media queries for larger screens:
-
-
-
-
-
`
`
sm
`
md`
`lg
`
`
xl`
`2xl`
: 640px — large phones, landscape
: 768px — tablets, portrait
: 1024px — tablets landscape, small laptops
: 1280px — desktops
: 1536px — large desktops
```
css
/* Mobile first — no media query needed for base styles */
.container { padding: 16px; }
/* Scale up */
@media (min-width: 768px) { .container { padding: 24px; } }
@media (min-width: 1024px) { .container { padding: 32px; } }
```
## Fluid Layout
- Use relative units (`%`
,
`fr
`
`
`
,
vw
,
`
vh`
`
,
rem
`) over fixed pixels for layout
- Use
`
max-width`
with auto margins for content containers instead of fixed widths
- Use CSS Grid with `
auto-fit`/`
auto-fill`
and `
minmax()` for responsive grids
without media queries
- Use Flexbox with `flex-wrap
` for flowing content
- Avoid fixed heights — let content determine element height
- Use
`
min()`
,
`
max()`
`
,
clamp()` for fluid sizing:
`
width: min(100%, 1200px)`
## Touch Targets
- Minimum touch target size: 44×44px (Apple) / 48×48px (Material)
- Add padding to small interactive elements to expand the tap area without changing
visual size
- Space touch targets at least 8px apart to prevent accidental taps
- Make entire list rows/cards tappable, not just the text within them
- Increase button padding on mobile: at least 12px vertical, 16px horizontal
## Responsive Typography
- Use a fluid type scale with `
clamp()`
:
- Body:
`
clamp(1rem, 0.95rem + 0.25vw, 1.125rem)` (16px → 18px)
- H3:
`
clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)` (20px → 24px)
- H2:
`
clamp(1.5rem, 1.2rem + 1vw, 2rem)` (24px → 32px)
- H1:
`
clamp(2rem, 1.5rem + 1.5vw, 3rem)` (32px → 48px)
- Reduce heading sizes on mobile — a desktop h1 shouldn't dominate a phone screen
- Adjust line-height for screen size: tighter on mobile (1.4), more relaxed on
desktop (1.6)
- Cap line length at ~75 characters on desktop — don't let text run full-width on
wide screens
## Images & Media
- Use
- Use
- Use
- Use
`
max-width: 100%; height: auto
`
on all images
`<picture>`
with `
srcset` to serve appropriately-sized images per screen
`
aspect-ratio
` to prevent layout shift while images load
`
object-fit: cover
` for images that need to fill a container without distortion
- Lazy load images below the fold with `loading="lazy"`
## Navigation Patterns
- Mobile: hamburger menu, bottom tab bar, or slide-out drawer
- Tablet: collapsible sidebar or compact horizontal nav
- Desktop: full sidebar, horizontal nav bar, or mega menu
- Don't hide critical navigation on any screen size — adapt it, don't remove it
## Common Patterns
- **Cards grid**: Use
`
auto-fit`
with `
minmax()`
— cards reflow naturally without
breakpoints
- **Sidebar + content**: Stack on mobile, side-by-side on tablet+
- **Tables**: Horizontal scroll on mobile, or reformat as stacked cards
- **Forms**: Full-width inputs on mobile, multi-column on desktop
- **Hero sections**: Reduce vertical padding and image sizes on mobile
- **Modals**: Full-screen on mobile, centered overlay on desktop