---
name: forms
description: "Teach Claude to build forms that feel good to use. Drop this file into your project root so Claude handles validation, error messages, loading states, and multi-step flows correctly — not just the happy path."
---
 
# Form Conventions
Follow these form conventions for all UI work in this project. Forms are where users
give you their data and trust — get them right.
## Input Basics
- Every input must have a visible
`<label>`
— not just placeholder text
- Use the correct `type
`
attribute:
`
email`
,
`
password`
,
`tel`
,
`
url`
,
`
number
`
,
`
search`
,
`date
`
- Set `inputmode
` for mobile keyboards:
`
numeric
`
,
`decimal`
,
`tel`
`
,
email`
,
`
url`
- Set `
autocomplete
`
attributes for common fields:
`
`
`
name
,
email`
,
`tel`
`
,
street-
address
`
,
`
postal-code
`
`
,
cc-number
`
`
- Use
required` for required fields, mark them visually with an asterisk and `
aria-
required="true"`
- Placeholder text is supplementary, never a replacement for labels
## Validation
### Timing
- Validate on blur (when user leaves the field), not on every keystroke
- Don't show errors before the user has interacted with the field
- After showing an error, re-validate on input so the error clears as soon as the
user fixes it
- Validate the full form again on submit
### Error Messages
- Place error messages directly below the input, not in a banner at the top
- Be specific: "Email must include @" is better than "Invalid email"
- Be helpful: "Password needs at least 8 characters" not "Password too short"
`
- Use
aria-describedby
` to associate error messages with inputs
- Use
`
aria-invalid="true"`
on fields with errors
- Use red for error styling but never color alone — add an icon or text
### Inline Validation
```
✓ Email format: validate on blur
✓ Password strength: validate on input (show strength meter)
✓ Username availability: validate on blur with debounce (500ms)
✗ Don't validate empty required fields until submit or blur
```
## Layout
- One column for most forms — don't make users zigzag
- Two columns only for naturally paired fields: first/last name, city/state,
start/end date
- Group related fields with `<fieldset>`
and `<legend>`
- Full-width inputs on mobile, max-width of ~400px on desktop
- Consistent spacing: 24px between field groups, 16px between label and input, 8px
between input and helper text
- Primary action button should be full-width on mobile, left-aligned on desktop
## Button States
- **Default**: Clear label describing the action ("Create Account"
, not "Submit")
- **Loading**: Disable the button, show a spinner, keep the label ("Creating
Account...
")
- **Success**: Brief confirmation before redirect or state change
- **Error**: Re-enable the button, show error message, don't clear the form
- Never use "Submit" as a button label — describe the action
## Multi-Step Forms
- Show a progress indicator (step 1 of 3, or a progress bar)
- Allow going back to previous steps without losing data
- Validate each step before allowing progression
- Save progress if possible (localStorage or server)
- Show a summary/review step before final submission
- Keep the most important/easiest step first to build momentum
## Error Recovery
- Never clear the form after a submission error
- Scroll to and focus the first field with an error
- If the error is server-side (network failure), show a retry option
- For destructive actions, require explicit confirmation (type the name to delete,
etc.)
## Field-Specific Patterns
### Password Fields
- Show/hide toggle for password visibility
- Show strength indicator during creation (not login)
- Don't set maxlength on passwords
- Confirm password field for signup, not for login
### Search
- No submit button needed — search on input with debounce (300ms)
- Show clear button (×) when field has content
- Show recent searches or suggestions in a dropdown
- Use
`type="search"`
and `
role="search"`
on the form
### File Upload
- Show accepted file types and size limits before selection
- Preview images after selection
- Show upload progress for large files
- Allow drag-and-drop alongside the file picker button
- Handle errors: wrong type, too large, upload failure
### Addresses
- Use autocomplete APIs when available
- Break into logical fields: street, city, state/province, postal code, country
- Adapt field labels and formats to the selected country
## Mobile Considerations
- Inputs should be at least 44px tall for easy tapping
- Use appropriate
`inputmode
`
so the right keyboard appears
- Avoid dropdowns for fewer than 5 options — use radio buttons or segmented controls
- Place labels above inputs, not beside them
- Stick the submit button to the bottom of the viewport for long forms
- Disable zoom on input focus with `<meta name="viewport" content="width=device-
width, initial-scale=1, maximum-scale=1">`