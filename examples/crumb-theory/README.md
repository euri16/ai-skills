# Example workspace profile: Crumb Theory

A complete brand profile for an example creator, so you can see what each workspace file holds and which skills read it.

**Crumb Theory is fictional.** It was invented for this repository: there is no real creator, account or business behind it, and every piece, date and test in it is made up. It is a creator of short vertical videos (Instagram Reels, TikTok, YouTube Shorts) that explain the science behind home baking, for curious home bakers. The files call the person on camera "the creator".

## Use it

1. Copy everything in this folder to the top level of your workspace, the folder your agent works in: `cp -R examples/crumb-theory/. <your-workspace>/`. `CONVENTIONS.md`, next to this repository's README, explains the layout.
2. Rewrite every file with your own brand. Keep the file names, the channel headings and the `piece.md` field names, since the skills read them; the opening line of each file says which skills those are.
3. Delete the example piece in `social/` and its row in `social/index.md` once you have your own.
4. Add your brand files to `brand-guide/assets/` (see below).

## Brand assets

- **Fonts:** `brand-guide/assets/fonts/fonts.css` loads Fraunces and Work Sans from Google Fonts (both under the SIL Open Font License) and exposes `--font-display`, `--font-text` and `--font-mono`. Point it at your fonts. For offline video renders, download the font files into the same folder and switch to the local `@font-face` rules commented in the file.
- **Logo, icons and textures:** not included. Put yours in `brand-guide/assets/logo/`, `brand-guide/assets/icons/` and `brand-guide/assets/textures/`. `brand-guide/visual-identity.md` lists the file names this example expects, so you can see how the skills refer to them.
- **Writing playbook:** `brand-guide/writing-style-playbook.md` is optional (see `CONVENTIONS.md`) and not part of this example.

The example piece folder holds only its record: the script, footage, cover and export it names are not included.

## Files

| File | What it holds | Read by |
|---|---|---|
| `brand-guide/positioning.md` | Territory, promise, differentiators, what the brand is not, independence | research-content-topic |
| `brand-guide/audiences.md` | Primary and secondary viewers, what they need, the order of an explanation | recommend-video-hook, write-short-video-script, research-content-topic |
| `brand-guide/voice-and-humor.md` | Voice traits, humor sources and limits, language, words to avoid | write-short-video-script, recommend-video-hook, write-caption, edit-short-video |
| `brand-guide/visual-identity.md` | Palette with roles and contrast, accent rule, typography, logo, icons, textures, graphics line, video tokens, review checklist | design-reel-cover, edit-short-video, generate-ai-images, analyze-video, find-video-audio |
| `brand-guide/motion.md` | Motion principles with the brand's numbers, sound identity | edit-short-video |
| `brand-guide/visual-ideation.md` | Optional brainstorm of visual directions before proposing visuals | write-short-video-script, edit-short-video, design-reel-cover |
| `brand-guide/assets/fonts/fonts.css` | Font loading and font variables | design-reel-cover, edit-short-video |
| `editorial/pillars.md` | The five content pillars | research-content-topic, write-short-video-script |
| `editorial/instagram.md` | Structure, length, production and captions for Reels, TikTok and Shorts | recommend-video-hook, write-short-video-script, write-caption |
| `operations/research-policy.md` | Claims that need a source, ranked sources, kitchen test protocol, claims ledger, food safety | research-content-topic |
| `operations/review-and-approval.md` | The five checks and what needs explicit approval | write-short-video-script and every skill that asks for approval |
| `social/AGENTS.md` | Piece folder layout, the index and the `piece.md` format | the production and scheduling skills |
| `social/index.md` | One row per piece | recommend-video-hook, design-reel-cover, write-short-video-script, schedule-social-piece |
| `social/2026-11-16-soda-vs-powder/piece.md` | An example record, approved and ready to schedule | schedule-social-piece, write-caption, edit-short-video |
| `media/AGENTS.md` | Where new footage lands, reusable shots, study material, the sound library | edit-short-video, find-video-audio |
