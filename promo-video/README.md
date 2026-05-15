# Verb Trainer — Promotional Videos

## Files

| File | Description |
|------|-------------|
| `promo_video.mp4` | v1 — manual setup, Sequence cuts, 15s |
| `promo_video_v2.mp4` | v2 — skill-guided, TransitionSeries fade, 10s |
| `src/Root.tsx` | Main composition with all scenes |

## Generation Prompt

Create a promotional video for Verb Trainer (English irregular verb practice app). Use Remotion with React components. Use 30 FPS. Style: dark theme matching the web app (#0a0a0f bg, #6366f1 accent). Three scenes with Sequence:

1. (0-4s) Hook: "¿Quieres llevar tu inglés al siguiente nivel?" — spring scale entrance
2. (4-8s) Solution: "Descubre Verb Trainer y aprende inglés de forma sencilla y divertida" — slide up from below using interpolate
3. (8-10s) CTA: Logo "Verb Trainer" + tagline + GitHub repo link — spring logo, fade elements sequentially

Use best practices: loadFont from @remotion/google-fonts/Inter, TransitionSeries with fade() and springTiming(), Easing.bezier() curves, premountFor, useVideoConfig(), AbsoluteFill. No CSS transitions or animations.
