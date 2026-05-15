---
name: frontend-ui
description: Professional UI conventions for the English Verb Trainer static frontend
---

## Design Principles
- Professional, clean dark mode (not "AI dark")
- No emojis as UI elements — use SVG sprite (`<svg><use href="#icon-xxx"/></svg>`)
- Minimal, purposeful animations (no gratuitous confetti)
- Consistent spacing, typography, and color tokens
- Accessible: proper contrast, focus states, semantic HTML

## Color Palette
- Background: `#0a0a0f` (deep, not pure black)
- Surface: `#141419` (cards, inputs)
- Border: `#1e1e26`
- Text primary: `#e8e8ed`
- Text muted: `#6b6b7b`
- Accent: `#6366f1` (indigo)
- Success: `#22c55e` (green)
- Error: `#ef4444` (red)
- Warning: `#f59e0b` (amber)

## Typography
- Font: Inter (Google Fonts) — already loaded
- Headings: weight 700-800, tight letter-spacing
- Body: weight 400, 15-16px
- Labels: uppercase, 11px, weight 600, tracking 0.8px

## SVG Icon System
- SVG sprite in `<body>` with `<svg style="display:none"><defs>...</defs></svg>`
- Each icon is a `<symbol>` with `id="icon-{name}"`, 24x24 viewBox
- Usage: `<svg class="icon"><use href="#icon-{name}"/></svg>`
- CSS classes: `.icon` (16px), `.icon-lg` (20px), `.icon-sm` (14px)
- Color via `stroke:currentColor` — tint with `.icon-check` (green), `.icon-x` (red)
- Available icons: target, play, chart, book, refresh, trophy, check, x, flame, warning, star
- If an icon name does not exist, add a new `<symbol>` to the sprite

## Component Conventions
- Cards: rounded (12px), subtle border, glass effect via backdrop-blur
- Buttons: rounded (8px), clear hierarchy (primary/surface/muted)
- Inputs: bordered, focus ring in accent color
- Feedback: left-border accent style (green for correct, red for wrong)
- Wrong items: left-border accent, subtle background
- Score circle: 120px ring with double border effect
- Transitions: 200ms ease for interactive elements

## Animation Conventions
- Screen transitions: fadeIn 400ms ease (opacity 0→1, translateY 16px→0)
- Background orbs: blur 100px, 20s drift animation, opacity 0.1
- Success: subtle scale pulse (successPulse function, 500ms)
- No confetti, no gratuitous motion

## Accessibility
- Skip link at top of `<body>` for keyboard users
- `:focus-visible` outline on all interactive elements (2px solid accent, 2px offset)
- `<label for="...">` on all form inputs (not `<span>`)
- `role="progressbar"` with `aria-valuenow/min/max` on progress bars
- `role="alert"` and `aria-live="polite"` on feedback elements
- `role="heading"` and `aria-level` on title elements
- Progress bar aria values updated in JS on each render

## JS Conventions
- Use `innerHTML` instead of `textContent` when injecting SVG icons
- Template literals with `${}` for dynamic content
- Success animations: `successPulse()` instead of confetti
