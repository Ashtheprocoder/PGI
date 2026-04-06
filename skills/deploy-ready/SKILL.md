---
name: deploy-ready
description: "T each Claude to build things that are ready to ship. Drop this file into your project root so Claude includes proper meta tags, handles environment variables, adds error boundaries, and avoids common deployment gotchas."
---
 
# Deployment Readiness Conventions
Follow these practices to ensure the project is production-ready. Don't leave these
for later — build them in from the start.
## Meta Tags & SEO
Every page must include these meta tags:
```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page Title — Site Name</title>
<meta name="description" content="Concise page description under 160 characters">
<link rel="icon" href="/favicon.ico">
```
For shareable pages, also include Open Graph tags:
```html
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Page description">
<meta property="og:image" content="https://example.com/og-image.jpg">
<meta property="og:url" content="https://example.com/page">
<meta name="twitter:card" content="summary
large
_
_
image">
```
## Environment Variables
- Never hardcode API keys, secrets, or service URLs in source code
`
- Use
.env
` files for local development, environment variables in production
- Prefix client-side variables appropriately for the framework (`NEXT
PUBLIC
_
_
`
,
`VITE
`
, etc.)
_
- Include a
`
.env.example
` file listing all required variables with placeholder
values
- Add `
.env
` to
`
.gitignore
`
— never commit secrets
```
# .env.example
DATABASE
URL=postgres://localhost:5432/myapp
_
API
KEY=your-api-key-here
_
NEXT
PUBLIC
SITE
URL=http://localhost:3000
_
_
_
```
## Error Handling
- Add error boundaries at the page level (catch errors without crashing the entire
app)
- Show user-friendly error states — not stack traces, not blank screens
- Log errors to the console in development, to a service in production
- Handle network errors gracefully: show retry options, not just error messages
- Handle loading states explicitly — show skeletons or spinners while data loads
- Handle empty states — show helpful messages when there's no data yet
## Performance Basics
- Optimize images: use WebP/AVIF, compress, serve appropriate sizes
- Lazy load images and heavy components below the fold
- Minimize JavaScript bundle size — code-split by route
- Use proper caching headers for static assets
- Avoid layout shift: set explicit dimensions on images, use font-display: swap
- Test with Lighthouse — aim for 90+ on all categories
## Common Deployment Gotchas
### Build Issues
- Ensure all dependencies are in
`dependencies
`
, not just `devDependencies
` (if the
build server needs them)
- Test the production build locally before deploying (`
npm run build && npm run
preview
`)
- Fix all TypeScript errors and linting warnings — most platforms treat warnings as
errors
### Routing
- Configure your hosting platform for SPA routing (redirect all routes to
`index.html`) if using client-side routing
- Use trailing slash consistently — pick one convention and stick with it
- Set up proper 404 pages
### Assets
- Use relative paths or absolute paths from root — avoid paths that break in
subdirectories
- Ensure fonts load correctly in production (check CORS headers for self-hosted
fonts)
- Verify all images and assets are included in the build output
### API & Data
- Use environment-specific API URLs (don't hit localhost in production)
- Handle CORS properly — configure allowed origins on your API
- Add rate limiting for public-facing APIs
- Validate all user input on the server, not just the client
## Pre-Launch Checklist
Before deploying, verify:
- [ ] All environment variables are set in the hosting platform
- [ ] Production build completes without errors
- [ ] All pages render correctly in the built version
- [ ] Meta tags and OG images are present
- [ ] Error states are handled (try disconnecting network)
- [ ] No console errors or warnings in production build
- [ ] Favicon is set
- [ ] Loading performance is acceptable (Lighthouse audit)
- [ ] Links all work (no 404s)
- [ ] Forms submit correctly and show validation errors