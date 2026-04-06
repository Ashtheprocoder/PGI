---
name: ui-copy
description: "Teach Claude to write UI text that actually helps users. Drop this file into your project root so Claude writes clear error messages, useful empty states, concise labels, and action-oriented buttons — instead of generic placeholder text."
---
 
# UI Copy Conventions
Follow these writing conventions for all interface text in this project. Every word
on screen should help the user do something or understand something.
## Tone
- Clear over clever — don't sacrifice clarity for personality
- Confident but not bossy — guide, don't command
- Brief but not cold — be human, not robotic
- Consistent — pick a voice and stick with it across the entire app
## Button Labels
- Use action verbs that describe what happens: "Save Changes"
,
"Send Message"
,
"Create Project"
- Never use generic labels: "Submit"
,
"OK"
,
"Click Here"
,
"Yes"
- Match the button label to the context: "Delete Account" not just "Delete" when the
action is destructive
- For paired actions, make the distinction clear: "Save Draft" / "Publish" not "Save"
/ "Save"
- Keep labels to 1-3 words when possible
### Patterns
```
✓ "Create Account" (specific action)
✗ "Submit" (generic)
✓ "Save and Continue" (clear outcome)
✗ "Next" (vague)
✓ "Remove from Cart" (specific + context)
✗ "Remove" (ambiguous)
✓ "Sign In" (standard convention)
✗ "Log In to Your Account" (too long)
```
## Error Messages
- Say what went wrong in plain language
- Say how to fix it
- Never blame the user
- Never show raw error codes or stack traces
### Patterns
```
✓ "That email is already registered. Sign in instead?"
✗ "Error: duplicate key violation on users.email"
✓ "Password must be at least 8 characters"
✗ "Invalid password"
✓ "We couldn't reach the server. Check your connection and try again.
"
✗ "Error 503"
✓ "This file is too large (max 10MB). Try compressing it first.
✗ "Upload failed"
"
```
## Empty States
Empty states are a chance to guide the user, not just say "nothing here.
"
- Explain what will appear here once they take action
- Provide a clear call-to-action to get started
- Keep it encouraging, not apologetic
### Patterns
```
✓ "No projects yet. Create your first one to get started.
"
[Create Project] button
✓ "Your inbox is empty. Messages from your team will show up here.
"
✗ "No data found.
"
✗ "Nothing to display.
"
✗ "0 results"
```
## Loading States
- Tell the user what's happening, not just that something is happening
- For operations over 3 seconds, show progress or context
- Don't use "Loading...
" for everything
### Patterns
```
✓ "Saving your changes...
✗ "Loading...
"
"
✓ "Searching 1,200 files...
✗ "Please wait"
"
✓ "Uploading photo (3 of 7)...
✗ "Processing...
"
```
"
## Success Messages
- Confirm what happened
- Tell the user what comes next if relevant
- Keep it brief — don't over-celebrate
### Patterns
```
✓ "Changes saved"
✗ "Your changes have been successfully saved!"
✓ "Message sent. They'll get it in a few minutes.
✗ "Success! Your message was sent successfully!"
"
✓ "Account created. Check your email to verify.
"
✗ "Congratulations! You've successfully created your account!"
```
## Confirmation Dialogs
- State the consequence clearly in the title
- Give enough detail in the body to make a confident decision
- Make the destructive action label specific, not just "OK"
### Patterns
```
Title: "Delete this project?"
Body: "This will permanently delete 'My Portfolio' and all its files. This can't be
undone.
"
Actions: [Cancel] [Delete Project]
NOT:
Title: "Are you sure?"
Body: "This action cannot be undone.
Actions: [No] [Yes]
```
"
## Labels & Headings
- Use sentence case ("Account settings") not title case ("Account Settings") unless
it's a proper noun
- Navigation labels should be one or two words: "Settings"
,
"My Projects"
,
"Help"
- Form labels should be concise nouns: "Email"
,
"Full name"
,
"Phone number"
- Section headings should tell the user what they'll find: "Recent activity" not
"Section 3"
## Placeholder Text
- Placeholder text disappears on focus — never put essential information there
- Use it to show format examples: "name@example.com"
,
"DD/MM/YYYY"
- Keep it short — long placeholder text gets truncated on mobile
- Don't use it as a substitute for labels
## Helper Text
- Place below the input, above error messages
- Use it for requirements or context: "Must be at least 8 characters" or "We'll send
a confirmation code"
- Keep it to one line when possible
- Use a lighter/smaller text style to distinguish from labels
## Numbers & Dates
- Use relative time for recent events: "2 minutes ago"
,
"Yesterday"
- Use absolute dates for older events: "Jan 15, 2025"
- Format numbers for readability: "1,234" not "1234"
,
"$12.50" not "$12.5"
- Abbreviate large numbers: "1.2K followers" not "1,200 followers"
- Use the user's locale when possible
## Accessibility Notes
- All text should be actual text, not images of text
- Don't rely on color alone to convey meaning —
"Required" label is better than just
a red asterisk
- Screen reader text (`
aria-label`) should describe function, not appearance: "Close
dialog" not "X button"
- Link text should describe the destination: "View pricing" not "Click here"
