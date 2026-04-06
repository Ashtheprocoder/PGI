---
name: apple-hig
description: "Teach Claude to build macOS and iOS apps that feel native. Drop this file into your project root so Claude follows Apple’s Human Interface Guidelines for typography, icons, navigation, and platform conventions."
---
 
# Apple Human Interface Guidelines
Follow these Apple platform conventions for all UI work in this project. The goal is
to make the app feel native — like it belongs on the platform.
## Typography
- Use the system font (`
-apple-system
`
,
`BlinkMacSystemFont`
, or
`SF Pro
`
via
`font-
family: system-ui`)
- Use San Francisco's built-in text styles for hierarchy:
- Large Title: 34pt, bold
- Title 1: 28pt, bold
- Title 2: 22pt, bold
- Title 3: 20pt, semibold
- Headline: 17pt, semibold
- Body: 17pt, regular
- Callout: 16pt, regular
- Subhead: 15pt, regular
- Footnote: 13pt, regular
- Caption 1: 12pt, regular
- Caption 2: 11pt, regular
- Use SF Mono for code and monospaced content
- Support Dynamic Type — use relative sizing so text scales with user preferences
## Icons
- Use SF Symbols as the primary icon set — they match the system aesthetic and scale
with text
- SF Symbols have 9 weights and 3 scales — match icon weight to adjacent text weight
- Use filled variants for selected/active states, outlined for inactive
- For tab bars: use filled icons for the selected tab, outlined for unselected
- Maintain consistent icon sizes within the same context (toolbar, list rows, etc.)
## Colors
- Use Apple's semantic system colors which adapt to light/dark mode automatically:
- Labels:
`labelColor
`
`
,
secondaryLabelColor
`
,
`tertiaryLabelColor
`
,
`
quaternaryLabelColor
`
- Backgrounds:
`
systemBackground`
`
,
secondarySystemBackground`
,
`tertiarySystemBackground`
- System colors:
`
systemBlue
`
`
,
systemGreen
`
`
,
systemRed`
, etc.
- Use the system accent color for primary actions — respects user's accent color
preference
- Support both light and dark appearance — test in both
- Use vibrancy and translucency where appropriate (sidebars, toolbars)
## Navigation
### macOS
- Use a sidebar for top-level navigation in document or collection-based apps
- Toolbar at the top for actions — use the system toolbar style
- Use the standard window controls (close, minimize, zoom) — never hide or move them
- Support the menu bar — common actions should be accessible from menus with keyboard
shortcuts
- Use sheets for modal input, popovers for contextual info, alerts only for critical
decisions
### iOS
- Use a tab bar for top-level navigation (max 5 items)
- Use
`NavigationStack` for hierarchical drilling down
- Swipe-back gesture must always work for navigation
- Pull-to-refresh for updating content
- Use standard toolbar positions: navigation bar at top, tab bar at bottom, toolbar
above keyboard
## Layout
- Respect safe areas — never place interactive content under the notch, home
indicator, or status bar
- Use standard margins: 16pt on compact width, 20pt on regular width
- Align content to the system layout margins
- Use list insets and grouped table styles for settings-like screens
- Support all orientations unless there's a strong reason not to
## Interaction
- Use standard gestures: tap, long press, swipe, pinch, rotate
- Provide haptic feedback for significant actions (iOS)
- Support context menus (right-click on macOS, long press on iOS)
- Use standard selection patterns: single tap to select, edit mode for multi-select
- Destructive actions should be red and require confirmation
## Platform Conventions
- Use native controls (buttons, toggles, sliders, pickers) — don't build custom
versions of system components
- Match the system's corner radius for cards and containers (10pt on iOS, varies on
macOS)
- Use the standard alert/action sheet patterns for confirmations
- Support Handoff, drag and drop, and other system integration features where
relevant
- Follow the app lifecycle conventions: save state on background, restore on
foreground