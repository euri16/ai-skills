---
name: design-reel-cover
description: Design Instagram Reel covers with the workspace's visual identity from a video or a photo. Use when the user asks for a cover or thumbnail for a Reel or vertical video, when they want to improve an existing one or compare alternatives, or when it is necessary to check how a cover will look in the profile grid.
---

# Design Reel Cover

A cover exists for a single thing: that someone looking at the profile taps that video. In the feed and in the Reels tab the video plays by itself and the first second does the work; where the cover decides is the profile grid, in a tile about 120 px wide on the phone. Design for that size.

Write everything the user reads (chat, questions, option names) in the user's language, or the one the workspace instructions set; on-canvas text goes in the language of the piece.

The design rules, the order of work and the sizes below are defaults; the brand guide and the workspace instructions win when they say otherwise. Instagram's own figures (canvas, crops, interface zones) are not defaults.

The creator is the person who appears in the videos; the user is who decides and approves. The workspace layout (`social/<YYYY-MM-DD-slug>/`, `piece.md`, `source/`, `cover-src/`, `brand-guide/`) is described in the repo's `CONVENTIONS.md`.

## Prerequisites

Check these when the skill is invoked, before doing anything else. Check that environment variables are set without printing their values. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| The piece's recorded material in `social/<YYYY-MM-DD-slug>/source/` (camera take, b-roll, photos), or the photo the cover starts from | Yes | The cover comes from those assets (see "When the cover is made") | Placed there when the piece is edited; layout in "A piece folder" of `CONVENTIONS.md` in the ai-skills repo |
| `brand-guide/visual-identity.md` | Yes | Every brand value of the cover: background colors, accent, headline and label typefaces, headline case, what the subject of a cover is, logo, icon rules and the visual review checklist | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/visual-identity.md` there is a filled-in example |
| `brand-guide/assets/fonts/fonts.css` and the fonts it points at | Yes | Loading the headline and label typefaces in the cover's render; without them the "FONT NOT LOADED" band appears and the cover is not presented. Fonts are not bundled with this skill. A `fonts.css` that loads from the web (an `@import` of Google Fonts, as the example's does) needs network at render time. `compare.sh` only warns without it and labels its sheet in Helvetica | `@font-face` rules for the brand fonts, as described in `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/assets/fonts/fonts.css` there is an example |
| `brand-guide/assets/logo/` | No | The logo in a top corner of the cover | Put the brand's logo files there (a light version and, if the brand has one, an accent version) |
| `brand-guide/assets/icons/` | No | One or two stickers or glyphs; without it the cover carries none, since they are never hand-drawn | Put the brand's icons and stickers there (SVG or PNG), with a catalog image if there is one |
| `brand-guide/assets/textures/` | No | A textured background | Put the brand's textures there |
| `brand-guide/visual-ideation.md` | No | The visual ideation of 6 to 8 metaphors, when the user asks for it | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/visual-ideation.md` there is a filled-in example |
| `social/AGENTS.md` and `social/index.md` | No | Cover concepts already used and how the approved cover is archived | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/social/AGENTS.md` there is a filled-in example |
| `brand-guide/voice-and-humor.md` | No | Deciding whether the cover can carry a humorous label; without it, no such label is proposed | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/voice-and-humor.md` there is a filled-in example |
| `brand-guide/positioning.md` | No | The handle, when `visual-identity.md` puts one on covers; without it, ask the user | Write it following `CONVENTIONS.md` in the ai-skills repo |
| Skill `analyze-video` | Yes, when the cover starts from a video | Learning the video's content, extracting candidate frames (`analyze-video/scripts/frames.sh`) and the gesture search | Install the `analyze-video` skill from the ai-skills repo next to this one |
| macOS on Apple Silicon | Yes, to transcribe a video that has not been analyzed yet | Inherited from `analyze-video`, whose transcription runs only there; extracting frames with `frames.sh` works on any system with Chrome and ffmpeg | Cannot be installed; on another system, start from a transcript or a description the user provides |
| Skill `generate-ai-images` | No | Editing a real frame to get an expression or gesture, and realistic effects | Install the `generate-ai-images` skill from the ai-skills repo next to this one |
| Google Chrome | Yes | Rendering HTML to PNG (`scripts/render.sh`, also used by `compare.sh`) | Install Google Chrome; if the binary is not at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, export `CHROME_BIN=<path to the binary>` |
| `ffmpeg` and `ffprobe` | Yes | `inspect.sh` and `preview.sh` (detail crops, zones, grid and the 120 px tile) | `brew install ffmpeg`; on Linux, `sudo apt install ffmpeg` |
| `python3` | Yes | URL encoding in `render.sh` and `compare.sh` | Included in macOS; elsewhere, the system package manager |
| `uv` | Yes, when the concept has a cutout | Running `scripts/cutout.py` with `rembg[cpu]` for the subject cut out | `brew install uv` or `pip install uv` (other installers at https://docs.astral.sh/uv/) |
| Network access on the first cutout | Yes, once per model | `uv` downloads `rembg[cpu]` and rembg downloads the model it is asked for (`birefnet-portrait` by default, `isnet-general-use` for objects) to its model folder, `~/.u2net`; later runs work offline | Nothing to install: the first run caches them |
| `U2NET_HOME` | No | Another folder for rembg's models | `export U2NET_HOME=<folder>` |
| `cwebp` | No | Archiving the photos and cutouts of the approved cover as WebP; without it they are archived as PNG | `brew install webp`; on Linux, `sudo apt install webp` |
| `BRAND_DIR` | No | The brand folder whose `assets/fonts/fonts.css` `compare.sh` loads. Default `./brand-guide` from where the scripts run | `export BRAND_DIR=<path to brand-guide>` |
| `COMPARE_BG`, `COMPARE_INK`, `COMPARE_FONT`, `COMPARE_GRID_LABEL` | No | Background, text and outline color, label font and grid caption of the comparison sheet. Defaults: a neutral dark sheet (`#15171C`, `#F3F1EC`, Helvetica, "In the grid") | Export them with values from `brand-guide/visual-identity.md` and the caption in the user's language |

## When the cover is made

By default the cover is designed after the video exists: when the creator has already recorded the take and the material used in the edit (camera take, b-roll, photos) is in the piece's `source/`. The reason is that the cover then comes from those same assets, not from similar material or an earlier piece, so it promises what the video shows. If the user asks for a cover and the video is not recorded yet or the assets are not in the piece, say so and propose waiting; when the user or the workspace instructions prefer another order (a cover from a photo taken for it, for example), follow it.

If no frame of the take works for the concept (expression, framing, gesture, prop), propose to the user that the creator take a photo just for the cover, describing exactly which photo the concept calls for (expression, pose, framing, clothing, light, background). A real frame of the piece can also be edited with AI to get the expression or gesture the concept calls for, by invoking `generate-ai-images` through the skill tool (mode 1: the creator looks the same, it is compared with the real photo and presented marked as generated). Before that, search for the gesture in all takes with the gesture-search recipe of the `analyze-video` skill (`analyze-video/references/find-gesture.md`). The concept's realistic effects (an explosion, smoke, sparks) are generated with `generate-ai-images` (mode 2) and blended according to its `generate-ai-images/references/compose-effects.md`.

## Load context

- `brand-guide/visual-identity.md`: palette, typefaces, social graphics line, icons and visual review checklist. Every brand value in this skill (background colors, accent color, headline and label typefaces, headline case, logo, stickers, textures) comes from there, and so does the subject of a cover: what the brand's hero image is (the creator, the product, the result) and what the cover line for its channel says.
- The Reel's caption or `script.md`, so as not to repeat it and to know what the punchline is.
- The handle, only if `visual-identity.md` puts one on covers. Take it from the brand guide (`brand-guide/positioning.md` or wherever the workspace keeps its profile links); if it is not written there, ask the user instead of guessing.
- `social/AGENTS.md` and `social/index.md`: cover concepts already used and the recent balance of piece types. Do not repeat a concept from the index.

## Instagram specifications

These are Instagram's figures. When the piece goes to another network, work out that network's size, crops and zones with the user before composing, and generate one `cover-<channel>.png` per network with the same concept.

- Canvas: 1080×1920 (9:16), PNG or JPG in sRGB.
- The profile grid shows the central 3:4: 1080×1440, from y=240 to y=1680. Everything important (face, headline, prop, logo) goes inside that band. Whatever is outside is only seen when the Reel is opened.
- Inside the 3:4, leave at least 60 px of space on the sides and keep the text away from the tile's edges.
- The Reels interface zones during playback (top bar down to y 210, bottom block from y 1400 at its tallest and button column at x 945 to 1080 between y 1095 and 1850) apply to the video, not to the cover in the grid. Respect them in the video's first frame; in the cover, the headline can occupy the lower half of the 3:4.
- These figures (the 3:4 crop, the interface zones and the 60 px margin) have one source: the block of variables at the top of the drawing commands in `scripts/preview.sh`, which paints them on `-zones.png`. The guides of `assets/cover-example.html` repeat them. If Instagram changes its layout, the figures change there first and then here and in the example. Percentages from ad guidelines are not used: they describe the ads interface, not an organic Reel.
- In the feed, if the Reel is shared there, the crop can be 1:1 or 4:5 centered: keep face and headline near the horizontal center.

## Design rules

**Text**
- Headline of 4 to 6 words in total, counting kicker and headline (a kicker takes 1 to 3 of them). This is a recommendation, not a measured figure: in the 120 px tile, more words stop being readable, and a cover with no text leaves the tile without a promise.
- A single idea, in the case (uppercase or sentence case) that `visual-identity.md` sets for headlines.
- The text adds the promise or the tension; it does not repeat the caption or the first line of the video.
- Promise only what the video delivers. A misleading cover punishes retention, and retention does push reach.

**By piece type**
- Educational or demo: the result or the concrete topic ("A budget in 10 minutes", "Why your bread did not rise"). The image shows the result, the product, the screen or the creator explaining.
- Humor or meme: the moment of the setup or the reaction, never the punchline. If the joke depends on a reveal, the cover poses the question and the video answers it. Check every word and every prop: does it spoil it?
- Community or event: the place or recognizable people and the name of the event.

**Image**
- The subject of the cover is the one the brand guide names as its hero image: the creator for a personal brand built on a face, the product or the result for a brand built on what it makes (in Crumb Theory, the bake, with the creator's hands or face in support). If `visual-identity.md` does not say, ask the user and propose writing the answer there. Propose the concepts from that subject and vary the metaphor and composition, not the subject. A cover without it only if the user asks for it.
- A single focal point: the subject plus the headline. Nothing competes with them.
- When the creator is on the cover, a real expression, ideally talking or looking at the camera. Do not fake shock faces.
- The face alone does not guarantee taps and neither does saturated color: what reads at small size is the headline. Do not sacrifice legibility for drama.
- Outlines, arrows or circles help little; use them only when they point at something.
- An optional device, only when the brand's voice has humor (`brand-guide/voice-and-humor.md`): a funny detail of the video (a prop, a gesture, something out of place) commented on with a short label in the creator's voice, such as an arrow toward a half-eaten sandwich on the desk with "Lunch, day 3".

**Brand** (values from `brand-guide/visual-identity.md`)
- Follow the cover line of `visual-identity.md` (its social graphics section) for backgrounds, headline case, pills, strokes, shadows and stickers. Where it is silent, these defaults apply; they are the style of the worked example, not a rule above the brand guide: a dark or light brand background, the headline in the headline typeface with the keyword in the accent color (accent rule of `visual-identity.md`), and kickers and labels in the label typeface inside a pill, with the text color the brand sets for text on the accent.
- Real photos of the creator and of the product or result; an AI-edited photo only through `generate-ai-images` and with approval.
- Watch the weight of the accent: if several accent elements (kicker, headline word, prop) compete and none stands out, remove one, for example the kicker with an outline instead of a fill. This is decided case by case, it is not a fixed rule: when in doubt, show the user the piece with and without the change.
- Logo from `brand-guide/assets/logo/`, in the version and position the brand guide sets; by default light or in the accent color, in a top corner, inside the 3:4.
- One or two stickers or glyphs from the brand's icon set in `brand-guide/assets/icons/` (and its catalog image, if there is one). Insert them as `<img>` or, to tint a single-ink glyph in a palette color, as a CSS `mask` (see `.sticker` in the example). Never hand-draw a sticker that imitates the ones in the set or invent a new one without proposing it to the user. Do not mix with thin-line icons, 3D emojis or generic AI imagery.
- Textured background from `brand-guide/assets/textures/` if the brand has them. Low-resolution textures go blurred or very subtle, never sharp at full screen.

**Composition** (the same rules as the brand's static social graphics; if the workspace has a social graphics skill, its graphic system applies too)
- Default legibility floor: no text below 36 px on the 1080 canvas (40 px if it must read in the grid, see Composition resources), unless the brand guide sets its own minimum. Supporting text does not look tiny and does not compete with the headline.
- The headline can cross the subject (a shoulder, a hand, the edge of an object) if it looks good and reads completely. If it hinders reading or looks forced, shorten that line or move the photo. The face is never covered.
- Headline and supporting text in balanced lines, without a single word on the last line; force the break if needed.
- No shape, prop or sticker touches the headline or the supporting text.
- No dead space inside the 3:4: if the text block leaves a third empty, center it, enlarge the subject or add an element or a supporting line.

**Series**
- The grid is recognized by the branding (typography, palette, finish), not by repeating the same composition. Check with `preview.sh` and the neighboring covers that the new one is not a copy of the previous one.
- Only an explicit series (several episodes on the same topic) shares a composition, and only if the user asks for it.
- If the grid looks saturated, alternate designed covers with clean frames in the same style.

## Concept and system

Each cover is designed from its video. What repeats between covers is the branding; the concept and the composition are new every time, because each video tells something different. The brand should be recognizable, not the covers alike.

**Fixed in all (branding)**
- Palette, the headline and label typefaces and the accent rule of `visual-identity.md`.
- The graphic finish the brand guide describes (outlines, shadows, stickers, textures), and the logo visible inside the 3:4. A brand guide that describes none gets the finish of the worked example, proposed to the user on the first cover and written into `visual-identity.md` once approved.

**New in each one (concept)**
- The visual metaphor: which object, scene or situation sums up the video without resolving it. It can be a drawn prop (a calendar, a price tag, a timer, a chart), a real screen, a before and after, a contrast of scale, a reaction or a scene from the video as is.
- The composition: where the subject goes, at what size, whether cut out or in the full frame, where the headline goes and what fills the rest of the space.
- The graphic tone: more energy for humor and announcements, more calm for dense explanations.

Before composing, propose 2 to 3 different concepts in one line each (metaphor + composition + headline), or, if the user asks for the visual ideation of `brand-guide/visual-ideation.md`, explore 6 to 8 metaphors from different categories, show them all in the chat in one line each (metaphor + composition + headline), recommend the strongest for the piece type and wait for the user to approve which one or ones get composed. If the piece belongs to a series or the video already has a visual world, the cover continues it. Discard any concept that only changes the text of a previous cover. When presenting, deliver options that differ in concept, not just in colors or sizes.

## Composition resources

`assets/cover-example.html` is a worked example of the level of finish, not a mold to fill in. Its colors and font names are an example brand declared as CSS variables at the top: replace them with the values of `brand-guide/visual-identity.md`, and point the logo and icon variables to the real files in `brand-guide/assets/`. Its style (a sentence-case headline, a rotated pill, strokes with flat shadows, a person as the subject) is one finish among many: the brand guide decides the real one. Reuse its techniques when they serve the concept and the brand:

- Background: frame of the place, blurred and tinted with the dark background color, with an accent halo behind the subject.
- Subject cut out, large, with a light and accent outline; bleeding off one side so the straight edge of the cutout is not shown, and fading out toward the bottom.
- A person inside a frame or disc with the head coming out over the top: the body ends at a clean edge without covering the background. The frame can be just an outline (accent with a dark edge) so the setting stays visible. For head and body to join, the two layers of the cutout must have the same position on the canvas, with the outline applied before the cut.
- Graphic prop rotated a few degrees, with an outline and flat dark shadow, in front of the subject if the subject would cover it.
- Dark gradient behind the headline to cover clothing or background with text.
- Labels that must read in the grid: at least 40 px for the small line and 60 px for the main one; below that they only read when the Reel is opened.
- Kicker in a rotated accent pill and a two-line headline, the second larger, with a dark stroke and flat shadow.
- The guides (`?guides=1`: the 3:4 crop and the Reels interface zones) and the font-not-loaded warning: copy them into every new HTML.

For scenes that already tell the idea, the simple composition works better: real frame at full screen, headline over a dark bottom gradient inside the 3:4, logo and at most one sticker. It also helps to alternate in the grid.

## Flow

Commands below are run from the workspace root; `<skills>` is the folder where these skills are installed and `<work>` the piece's `cover-src/`.

1. **Define.** Piece type, promise and punchline that cannot be revealed. With that, draft 2 or 3 concepts (or, if the user asks for the visual ideation, explore the metaphors according to `brand-guide/visual-ideation.md`), each with its metaphor, composition and a 4 to 6 word headline. They are presented in step 2, together with the frames.
2. **Frames.** If the video has not been analyzed yet in this conversation, invoke `analyze-video` through the skill tool to learn its content (transcript, shots and contact sheet). For specific cover candidates, extract more timestamps with its script:
   ```bash
   <skills>/analyze-video/scripts/frames.sh "<video>" <work>/frames 1.75 8 17.9
   ```
   Open the candidates sheet together with its folder and present them with a recommendation: expression, sharpness, whether the key object is visible, whether burned-in subtitles get in the way (moments between sentences usually come out without subtitles). If the concept uses a setting background, choose that frame too.
   **Plan approval (mandatory).** Present the concepts, with the recommendation, and the frames together, and ask with the structured question tool of the agent in use (for example `AskUserQuestion`) which concept or concepts get composed and with which frame. Do not cut out, compose or render before that approval, unless the user expressly asks to skip this step.
3. **Cutout.** When the concept has the subject cut out:
   ```bash
   uv run --python 3.11 --with "rembg[cpu]" python <skills>/design-reel-cover/scripts/cutout.py <work>/frames/f_<t>.png <work>/cut.png
   ```
   The default model is made for a person. When the subject is an object, a product or food, add `--model isnet-general-use`. Review the cutout at full size: for a person, the fine edges (hair, accessories, hands) and the object they hold; for an object, thin parts, holes and its real outline.
4. **Compose.** Write the concept's HTML in the piece's `cover-src/` (alternative concepts in `cover-src/alt-<letter>/`, never in a temporary folder), starting from the example only where it helps (brand variables, fonts, guides, techniques). Draw the props the idea calls for (a calendar, a label, motion lines); stickers and glyphs always come from `brand-guide/assets/icons/`. Adjust the position and size of each element until everything is inside the 3:4, with nothing covering the face or hindering reading.
5. **Render.**
   ```bash
   <skills>/design-reel-cover/scripts/render.sh <work>/cover.html <work>/cover.png
   <skills>/design-reel-cover/scripts/render.sh <work>/cover.html <work>/guides.png 1080 1920 guides=1
   ```
   If the red "FONT NOT LOADED" band appears, the brand fonts failed: fix it before continuing. The usual causes, in order: the HTML's `<link>` to `fonts.css` has the wrong relative path (the example assumes three levels below the workspace root); `fonts.css` or a font file it points at is missing; `fonts.css` loads the fonts from the web and there is no network; or the family name in the HTML's `--font-headline` or `--font-label` is not the one `fonts.css` declares.
6. **Visual review (mandatory before showing anything).** The user must not find defects that a careful review would have caught. Review each option like a demanding designer and fix whatever fails before presenting it:
   ```bash
   <skills>/design-reel-cover/scripts/inspect.sh <work>/cover.png <work>/detail
   <skills>/design-reel-cover/scripts/preview.sh <work>/cover.png <work>/prev [left_neighbor.png] [right_neighbor.png]
   ```
   - **Detail at real size** (the 6 crops from `inspect.sh`, one by one; the whole cover is seen scaled down and hides defects):
     - Cutout edges: the fine edges of a person (hair, accessories, hands, ears) and the outline of an object, without halos, bites or leftovers of the original background.
     - Joins between the subject and the background: no murky blend, straight frame edge or outline that cuts off abruptly. If the body does not end cleanly, close it with a graphic device (frame, disc, band) instead of blurring it.
     - Loose fragments of the cutout or gaps (between arm and body, for example) with their own outline.
     - Text: spelling, accents and the punctuation of the piece's language (including opening question and exclamation marks in languages that use them), nothing covered by stickers, clean stroke and shadow; if it crosses the body, it reads completely and does not cover the face.
     - Composition: no text below the legibility floor, the accent does not saturate (case by case), balanced lines, no shape touches the text and no third of the 3:4 empty.
     - Elements that touch the canvas edge or overlap without intent.
   - **`-zones.png`:** nothing important outside the blue lines of the 3:4 crop.
   - **`-mini.png` (120 px):** the headline reads and what is happening is understood, with a single focal point.
   - **`-grid.png`:** works next to the profile's neighboring covers (pass the real ones if they exist) and is not a copy of them.
   - Visual review checklist of `brand-guide/visual-identity.md` and that "FONT NOT LOADED" did not appear.
   If anything is fixed, render again and repeat the full review. Only move to step 7 when all options pass it.
7. **Present.** Always show the options in a single image, side by side, with each one's letter and name, the full cover and its view in the grid:
   ```bash
   <skills>/design-reel-cover/scripts/compare.sh <work>/comparison.png "A · Split screen" <work>/a.png "B · Lunch, day 3" <work>/b.png
   ```
   Open that image and its folder for the user (on macOS, `open`), since images are not visible in the terminal. Explain in one line what each option does and recommend one. With a single option (for example, when iterating), open the cover directly.
8. **Iterate** on the chosen option with the changes the user asks for, repeating render and review.
9. **Record** the approved cover in `social/YYYY-MM-DD-slug/`, following `social/AGENTS.md` when the workspace has one: if `piece.md` does not exist yet, create it with the `- Hook:` line copied from `script.md` or `hooks.md` and put the hook's template code in the piece's index row; `cover-instagram.png` (`cover-<channel>.png` for another network) in the piece folder; `cover-src/` with the HTML and its images in relative paths (photos and cutouts in WebP with `cwebp -q 88 -alpha_q 100`, checking that the render still matches; PNG without `cwebp`); the Cover section of `piece.md` (concept, composition, headline, file) and the cover concept in the piece's row of `social/index.md`. Discarded alternatives are not part of the record: offer the user to move their `cover-src/alt-<letter>/` folders to the system Trash. One the user asks to keep stays in its `cover-src/alt-<letter>/` folder and is named in the Cover section.

## Deliver

- The final cover opened in the file manager, with its path in `social/`.
- Reminder for publishing: upload it as the Reel's cover ("Edit cover" on the share screen, adding the image from the camera roll) and, in that same cover editor, adjust the crop the profile grid will show ("Profile grid" in recent versions of the app) before publishing. Then check the grid. Changing the cover after publishing is not always available: review it before.
- Do not publish, schedule or upload anything without explicit approval from the user.

## Improving the skill

When a job confirms a better technique, a recurring composition problem, a change in how Instagram shows covers or a stable preference of the user, tell the user and propose where it belongs: a stable preference of this brand goes in the workspace's `brand-guide/visual-identity.md`, and a change to the method goes in this skill. Edit either only with the user's approval, never on your own: the installed skill is shared by every piece and is replaced when it is updated.
