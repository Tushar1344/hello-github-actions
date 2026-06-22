# Chip Design From the Bottom Up

**Live:** https://tushar1344.github.io/chip-design/

An interactive book that builds an AI accelerator from first principles — from a single
transistor acting as a switch, up to the systolic array at the heart of every TPU. It is a
reconstruction of the Dwarkesh Patel × Reiner Pope lecture
[*Chip design from the bottom up*](https://www.youtube.com/watch?v=oIk3R-sMX5o), reorganised so
that each concept builds on the previous one, with a live, pokeable simulation for every idea.

> Content is an original explanatory reconstruction from the lecture's published outline plus
> standard hardware fundamentals — not a verbatim transcript.

## Stack

- **Vite + React + TypeScript** single-page app
- **KaTeX** for LaTeX math (bundled locally — no CDN dependency)
- **SVG / React** interactive simulations
- **HyperFrames-style** HTML compositions rendered to MP4 in CI
- Design system ported from the [avianna.ai](https://github.com/Tushar1344/avianna) site
  (paper / ink / teal palette; Inter · Source Serif 4 · Chivo Mono)

## Develop

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # type-check + production build → dist/
npm run preview    # serve the production build
```

## Chapters (vertical slice)

1. **Logic Gates** — transistors as switches; building any function from `NAND`.
2. **The Multiply-Accumulate** — adders, multipliers, and the one op all of AI runs on.
3. **The Systolic Array** — tiling MACs into a grid that beats the data-movement wall.

Each chapter lives in `src/content/chapters/`; the registry is `src/content/chapters.ts`.
Chapters 4–11 (pipelining, cache vs scratchpad, FPGA vs ASIC, CPU/GPU/TPU, brains vs chips) are
the planned next phase.

## Video demos

The animated demos are authored as self-contained, *seekable* HTML compositions in
`public/compositions/<id>/index.html`. They:

- **play live in the browser** (auto-running `requestAnimationFrame` loop), and
- **render to MP4** deterministically via `window.seek(t)` + headless Chrome + FFmpeg.

`VideoDemo` serves `public/videos/<id>.mp4` when it exists, and falls back to the live HTML
composition otherwise — so demos work even before any video is rendered.

```bash
npm i puppeteer ffmpeg-static     # render-only deps
npm run render:videos             # → public/videos/*.mp4
```

In CI, the **Render HyperFrames video demos** workflow does this on a Chrome-equipped runner and
commits the MP4s back, which triggers a redeploy.

## Deployment

`.github/workflows/deploy.yml` builds the app and deploys it to **GitHub Pages**. Enable Pages
with the **GitHub Actions** source in repository settings. The site is served under
`/<repo-name>/` (the deploy workflow sets `VITE_BASE` from the repo name automatically);
`public/404.html` provides the SPA deep-link fallback.

## Theming

All colors, fonts, and spacing live as CSS custom properties in `src/theme/site.css` (`:root`).
Retarget the look by editing those tokens — nothing else needs to change.
