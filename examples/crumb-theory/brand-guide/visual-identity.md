# Visual identity

Palette, typography, logo system, graphic line and the visual review checklist of Crumb Theory. Read by `design-reel-cover` and `edit-short-video` for every brand value, by `generate-ai-images` for the palette, and by `analyze-video` and `find-video-audio` to color their review pages.

## Status

This file is the only source of truth for the visual brand: there is no separate manual. Gaps are collected under "Open decisions" below. A gap is filled by asking the user, never by guessing, and the answer is written here.

Brand files live in `assets/`. This example ships only `fonts/fonts.css`; logo, icon and texture files are yours to add. The sections below name the files the skills expect so you know where yours go.

## Visual idea

**The baker's notebook at night.** A dark, warm kitchen counter, flour-colored handwriting and one bright berry mark on the thing that matters. Pieces should feel like a page from a careful notebook: measured, annotated, a little handmade, never sterile and never cluttered.

- Dark warm backgrounds carry most pieces, so the bakes (golden crusts, pale crumbs) glow against them.
- The bake is the hero image. The creator's hands and face support it.
- Annotations look drawn with a steady hand: thin rules, measurement ticks, arrows, labels. They come from `assets/icons/`, never improvised.

## Palette

Six tokens. Use exactly these values. There is no pure white or pure black in the brand: Flour is the light, Rye is the dark.

| Token | HEX | RGB | Role |
|---|---|---|---|
| Rye | `#2A211B` | 42, 33, 27 | Main dark background: video backgrounds, covers, carousels, subtitle boxes, window bars |
| Crust | `#6B4A33` | 107, 74, 51 | Dark surface: cards, code and screenshot windows, flat headline shadows on covers |
| Flour | `#F7F1E6` | 247, 241, 230 | Light background, and text on every dark surface and on Berry |
| Berry | `#C23B5A` | 194, 59, 90 | The one composition accent: key word, pills, CTA, the variable under test |
| Sage | `#7A8F5C` | 122, 143, 92 | Secondary: the control in a comparison, icons, chart marks, neutral glow |
| Butter | `#F2D27A` | 242, 210, 122 | Small highlights only: a figure, an underline, a tick, a sparkle |

### Contrast

WCAG 2.x contrast ratios, computed from the HEX values above with the relative luminance formula. Level AA needs at least 4.5 for body-size text, and 3.0 for large text, icons and other graphics.

Recommended text pairs:

| Text on background | Ratio | Use |
|---|---|---|
| Flour on Rye | 14.03 | Any size. The main reading pair |
| Rye on Flour | 14.03 | Any size. Light backgrounds |
| Butter on Rye | 10.72 | Any size, for small highlights only (a figure, a label) |
| Rye on Butter | 10.72 | Any size. Text on a small Butter tag |
| Flour on Crust | 7.04 | Any size. Cards and windows |
| Crust on Flour | 7.04 | Any size. Secondary text on light backgrounds |
| Butter on Crust | 5.38 | Any size, for small highlights on cards |
| Flour on Berry | 4.59 | Any size. **The standard text on Berry** (pills, CTA, highlight blocks) |
| Berry on Flour | 4.59 | Any size. Accent word on light backgrounds |

Large text and graphic elements only:

| Pair | Ratio | Use |
|---|---|---|
| Sage on Rye, Rye on Sage | 4.44 | Large labels, icons, chart marks |
| Flour on Sage, Sage on Flour | 3.16 | Large labels, icons, chart marks |
| Berry on Rye | 3.05 | Display headline words and graphic marks only (see the accent rule) |

Never as text:

| Pair | Ratio | Why |
|---|---|---|
| Crust on Rye | 1.99 | Surface on background only, for cards and depth |
| Berry on Crust | 1.53 | Disappears; put Berry on Rye or Flour instead |
| Sage on Crust | 2.23 | Too low for any text |
| Butter on Flour, Flour on Butter | 1.31 | Invisible |
| Rye on Berry | 3.05 | Readable only when large, and text on Berry is always Flour |
| Berry on Butter | 3.51 | Two warm accents fighting; never pair them |

### Accent rule

- **Berry is the only accent.** One Berry element leads each frame or slide: the key word of a headline, a pill, the CTA, or the bowl that has the changed ingredient. If two things are Berry, one of them is wrong.
- **Text on Berry is Flour,** never Rye and never Butter.
- **Berry as text on Rye only when large:** headline words in Fraunces at 96 px or more and subtitle key words in Work Sans 700 at 64 px or more, both on a 1080 px wide canvas (the 3.05 ratio passes only as large text). Smaller accent text sits on a Berry block with Flour text, or the highlight moves to Butter.
- **One Berry voice per frame:** when a subtitle key word, a headline word and a pill would all be Berry at once, keep the most important one and turn the subtitle word back to Flour.
- **Sage is not a second accent.** It marks the control, a confirmed result or a neutral element, always quieter than Berry.
- **Butter stays small.** Never a background larger than a label, never a gradient, never next to Berry.
- **No extra red, green or blue.** A failed result is shown with its photo and its label, not with a warning red. A good result is Sage, not a new green.
- **Gradients:** only Rye to Crust (vignettes, depth behind a cutout). No other gradients.

## Typography

| Role | Family | Weights and settings | Fallback |
|---|---|---|---|
| Display: headlines, giant numbers, wordmark | **Fraunces** (variable soft serif) | 600 to 700 for headlines, 800 for giant numbers; optical size at its largest for display text | Georgia, serif |
| Text: subtitles, pills, labels, body | **Work Sans** (variable sans) | 400 body, 600 pills and labels, 700 subtitles | system-ui, Arial, sans-serif |
| Monospace: recipes as data, timers, code | System monospace stack | Regular | ui-monospace, Menlo, monospace |

- Both families are on Google Fonts under the SIL Open Font License 1.1, so they can be used, embedded and redistributed with the project.
- `assets/fonts/fonts.css` loads both and exposes `--font-display`, `--font-text` and `--font-mono`. Link it from any HTML (covers, edit projects, review pages). It loads from Google Fonts; its header explains how to switch to local files for offline renders.
- Verify in the render that Fraunces and Work Sans actually loaded before presenting anything as brand typography. If they did not, say so.
- Headlines in sentence case. Labels and pills may use small caps or uppercase with slight letter spacing in Work Sans 600.
- Never a third family. Never Fraunces for subtitles or long text.

## Logo system

Files go in `assets/logo/`. They are not part of this example; these are the names the skills and this file expect:

| File | What it is | Where |
|---|---|---|
| `wordmark-flour.svg`, `wordmark-rye.svg` | "Crumb Theory" set in Fraunces 700 on one line | End cards, channel banners, carousel last slides |
| `monogram-flour.svg`, `monogram-berry.svg`, `monogram-rye.svg` | The letters "ct" in Fraunces inside a rounded square | Avatars, cover corners, carousel corners, watermarks |

Export a PNG of a monogram next to its SVG when a tool needs a raster file.

- Clear space: at least the height of the letter "c" of the mark on every side.
- Minimum size: monogram 64 px wide on a 1080 px canvas; wordmark 280 px wide.
- On Rye or Crust, the Flour version; on Flour, the Rye version; Berry version only on Rye.
- Video carries no logo on screen. Covers and carousels carry the monogram in a top corner.
- Never recolor, stretch, outline, shadow or rebuild the mark with another typeface.

## Icons and stickers

Files go in `assets/icons/` as single-ink SVGs, drawn with rounded line ends and one stroke weight across the set. Expected set:

`whisk.svg`, `timer.svg`, `thermometer.svg`, `scale.svg`, `spoon.svg`, `bubbles.svg`, `crumb.svg`, `arrow.svg`, `sparkle.svg`, `focus-corners.svg`, `check.svg`, `question.svg`

- One or two per piece. They point at or label something; they are not decoration.
- Single ink in Flour, Butter or Sage; Berry only when the icon is the accent of the frame.
- Icons come from this folder, not from improvised drawing. A missing icon is designed, shown to the user and saved here before it is used.
- No emoji-style 3D icons, stock clip art or mixed icon styles in the same piece.

## Textures

Optional files in `assets/textures/`:

- `flour-grain.png`: a fine grain overlay for Rye backgrounds, at low opacity (around 6 to 10 %).
- `parchment.jpg`: a light paper texture for Flour backgrounds.

Without them, use flat Rye or flat Flour. A texture never sits behind small text at a strength that makes the text harder to read.

## Photography and footage

- Real bakes only. A result shown as the outcome of a test is always the real result, filmed or photographed in the creator's kitchen.
- True color: warm light is welcome, but no filter that changes the color of a crust or crumb, because browning is often the evidence.
- Cross-sections are filmed close and sharp, cut with a serrated knife after cooling, against a Rye or Flour surface.
- Side-by-side tests are framed so both samples are the same size in frame, lit the same way and labeled.
- Generated images never stand in for a bake result. They may add effects (steam, a flour puff) or show an illustration of what happens inside a dough, labeled as an illustration and approved by the user (`generate-ai-images`).

## Social graphics line

How brand pieces look across formats:

- **Background:** Rye with the optional grain, or Flour for light pieces such as carousels with a lot of text.
- **Headline:** Fraunces in Flour on Rye (or Rye on Flour), one key word in Berry following the accent rule. Short: one idea, ideally four to six words.
- **Pills and labels:** Work Sans 600, either a Berry pill with Flour text or an outlined pill in Flour. Labels for comparisons use the same words every time: "Test" for the changed sample, "Control" for the reference.
- **Comparisons:** the tested variable is marked in Berry, the control in Sage, both labeled. Never a comparison without labels.
- **Hero image:** the bake, filling at least half of the frame, with the creator's hands or face when they add reaction or scale.
- **Annotations:** thin Flour rules and arrows from the icon set, measurement ticks and Butter for the one figure that matters.
- **Signature:** the monogram in a top corner on covers and carousels. No handle in the artwork; the platform already shows it.

By channel:

| Channel | Application |
|---|---|
| Reel, TikTok and Short covers | Rye background or a darkened frame of the bake, headline in Fraunces with one Berry word, the bake in the center third, monogram in a top corner |
| On-screen text in short video | Subtitles in Work Sans 700, Flour on a Rye box, key word in Berry; beat headlines in Fraunces; pills in Berry with Flour text; Butter for the one figure that must stick |
| Carousels and image posts | Flour or Rye background, one idea per slide, the bake photo on the first slide, monogram on the first and last |
| Stories | Rye background, large Work Sans text, one Berry element per frame |

## Tokens for video and HTML

The palette mapped to the roles that `edit-short-video` (its "Brand tokens" table), `design-reel-cover` and the review pages of `analyze-video` and `find-video-audio` name. Paste the block into a project's `assets/brand.css`, or copy the values into a cover's `:root`.

| Role | Token | Value |
|---|---|---|
| Dark background: brand background, subtitle box, darkening | Rye | `#2A211B` |
| Deep ink: window bars, depth layers | Rye | `#2A211B` |
| Text on the accent | Flour | `#F7F1E6` |
| Mid tone: neutral glow, texture strokes, control marks | Sage | `#7A8F5C` |
| Accent | Berry | `#C23B5A` |
| Light neutral: code text, window dots, light backgrounds | Flour | `#F7F1E6` |
| Text on dark: subtitles, headlines (the brand has no pure white) | Flour | `#F7F1E6` |
| Code, screenshot and card windows; flat headline shadow on covers | Crust | `#6B4A33` |
| Secondary ink for drawn props | Sage | `#7A8F5C` |
| Small highlight | Butter | `#F2D27A` |
| Display font | Fraunces | 700 |
| Text font | Work Sans | variable, 400 to 700 |
| Monospace | system stack | ui-monospace, SF Mono, Menlo |

```css
:root{
  --bg:#2A211B;            /* Rye */
  --bg-rgb:42,33,27;
  --ink:#2A211B;           /* Rye: window bars, depth layers */
  --on-accent:#F7F1E6;     /* Flour: text on Berry */
  --mid:#7A8F5C;           /* Sage */
  --accent:#C23B5A;        /* Berry */
  --accent-rgb:194,59,90;
  --light:#F7F1E6;         /* Flour */
  --text:#F7F1E6;          /* Flour: subtitles and headlines on dark */
  --code-bg:#6B4A33;       /* Crust */
  --highlight:#F2D27A;     /* Butter */
  --font-display:"Fraunces";
  --font-text:"Work Sans";
  --font-mono:ui-monospace,"SF Mono",Menlo,monospace;
}
```

## Visual review checklist

Run through this list before showing a cover, frame, slide or graphic:

- Only the six palette colors; no pure white, pure black or extra reds and greens.
- One Berry element leads the frame; text on Berry is Flour.
- Every text pair is in the recommended contrast table at its size.
- Fraunces and Work Sans loaded in the render.
- Monogram from `assets/logo/` in the right version for the background, at or above the minimum size, with its clear space.
- Icons from `assets/icons/`, one or two per piece.
- Bake results are real footage or photos, in true color; generated images labeled and approved.
- Comparisons labeled "Test" and "Control", with the variable in Berry and the control in Sage.
- Quantities and temperatures on screen are correct and carry their units.
- Legible on a phone, outside the platform's interface zones.

## Open decisions

- Final logo artwork: the description above is the brief, not a finished design.
- A light-background version of the video subtitle style.
- Templates for carousel interiors with recipes as data tables.
- Logo animation for end cards (see `motion.md`).
