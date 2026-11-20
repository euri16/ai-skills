# Short video editing system

Operational source for the finish. The concrete brand values (colors, fonts, logo, textures, icons, motion character) come from the workspace's `brand-guide/visual-identity.md` and `brand-guide/motion.md`; what is in neither this file nor the brand guide is proposed to the user before using it. Where another file of this skill repeats a number, this file is the one that decides inside the skill. Everything here is a default: where the brand guide or the workspace instructions set another value or another rule (a subtitle position, a logo, a closing card, a speed), theirs wins and the proposal says so.

Two assumptions run through the file. The safe zones are measured on Instagram, the most restrictive of the four platforms for organic video, and are used as the conservative default for all of them; a piece made for one other platform can use that platform's zone from `quality-control.md`. The rules counted in words (subtitle blocks, headline lengths) assume a language written with spaces between words; for a language without them, set the limits in characters, starting from the 24 characters per subtitle line and the reading ceiling of "Subtitles".

## Brand tokens

The rules below name colors and fonts by role. Map each role to the values of `brand-guide/visual-identity.md` once per piece, in the project's `assets/brand.css` ("Project" in `hyperframes-recipes.md`), whose tokens every recipe reads.

| Role | What it is for | Token in the project CSS |
|---|---|---|
| Dark background | Brand background, subtitle box, pills of the hook, card shadows, darkening | `--bg` (and `--bg-rgb`) |
| Deep ink | Window bars, depth layers, window background when `--code-bg` is not set | `--ink` |
| On accent | Text on the accent color | `--on-accent` |
| Mid tone | Neutral glow, texture strokes | `--mid` |
| Accent | Key words, giant typography, pills, highlights, the glow of the twist | `--accent` (and `--accent-rgb`); a logo-only variant of the accent, if the brand has one, stays inside the logo |
| Light neutral | Window dots, text inside windows | `--light` |
| White | Subtitles, headlines: the brand's text color on dark backgrounds, pure white unless the brand sets another | `--text` |
| Display font | Headlines and figures | `--font-display` |
| Text font | Subtitles, pills and labels | `--font-text` |
| Monospace (optional) | Code, commands or data in lines, in pieces that show them | `--font-mono`: the brand's monospace, or a system monospace stack if the brand sets none |
| Window background (optional) | Windows with code or data and card windows | `--code-bg` |
| Logo, texture, icons | Brand background, arrows and pointers | files in `brand-guide/assets/logo/`, `textures/` and `icons/`, when the brand has them |

No color outside the palette of `visual-identity.md`.

## Principle

An effect earns its place when it points at what is being said (a color, an arrow, a highlight), reveals it in parts and arrives in sync with the word. An effect looks cheap when it runs alongside the content without referring to it: zoom on every phrase, whoosh on every cut, emojis, generic b-roll, text that repeats the voice, music that competes, default fonts, linear motion, long animations or bounce on everything.

- **The creator on camera, the visuals around them.** As a general rule, the creator is on camera and the visuals happen around them instead of cutting from them to the graphic. Record wider (space at the sides and above the head) so the visuals float in that free space, next to the head, over the shoulder or below, with a soft shadow so they feel part of the scene; in two or three sections per piece they can pass behind the creator with the brand background cutout. The creator looks at the camera practically always, so recording is as simple as a talking head: the edit places the visuals in the free space without depending on their gaze. A gesture or a look toward the visual is optional and is only marked in the script if the creator asks for it. It is the general rule, not a prohibition: there are visual-only full-screen moments when they add something, for example a screenshot with text, a demo, a b-roll that tells something or a pause that resets the pace, and they are decided in the edit proposal.

## Screen layouts

Three ways of dividing the frame: two for pieces with the creator on camera and a third for pieces without a camera take. One is chosen per piece in the edit proposal and kept; changing layout mid-video is a device, not an oversight, and it is marked.

1. **Visuals around the creator (default).** The creator to camera and the visuals float around them or pass behind them, as the principle above describes.

2. **Split view (pieces with a lot of b-roll).** B-roll on top, subtitle at the seam and the creator below in a camera card from which their head sticks out. For videos where every line has its screen (demos, news with sources, step-by-step explanations with screenshots, a graphic every 3 to 5 s) and the face accompanies more than it leads. Not for opinion or sketch.
   - **Construction.** B-roll canvas from y 240, graphics centered at 70 to 85 % of the width over the dark background with the brand texture, if it has one, and a soft glow behind the graphic. Camera card at full width from its edge to the bottom edge, with rounded top corners (radius 80) and no bottom border. Its depth is a diffuse shadow it casts on the background (upward, about 18 px offset and 56 px blur, black at 60 %), in a layer behind the take, with no edge highlight or stroke; the cut-out head stays in front. The creator's head comes out of the card: two layers of the same take aligned pixel by pixel, the card (full take with its room, masked) and the creator's cutout (`hyperframes remove-background`) visible only above the edge; the card edge passes at eyebrow height, so the hair and the whole forehead stick out. The cutout, with a soft edge, no halo, shadow or stroke. If the cutout fails in the first render (look at the fine edges: hair, accessories and hands), the card goes without the head sticking out and this is flagged in the review. Record with the head in the upper third and space at the sides; the take is shifted until the eyebrows are at the height of the card edge and zoomed in as needed for the body to reach the bottom edge; above the edge nothing of the take is seen except the cut-out head.
   - **Variant 2a, subtitle at the seam.** Card edge at y 1115 (58 %), at eyebrow height, with the eyes just below. Subtitle at the seam between the b-roll and the head, vertically centered between the bottom edge of the b-roll and the top of the hair (the space map measures it), never over the face: it is the planned exception to "always below the face", because under the chin it would end below the y 1400 limit. B-roll from y 240 to 706 at 85 % of the width.
   - **Variant 2b, subtitle below the face.** Card edge between y 960 and 1000 (50 to 52 %), at eyebrow height, with the eyes just below. Subtitle under the chin with 40 px of space, in the standard position of "Subtitles" (bottom edge at y 1400 or above). If the chin sits too low for that, raise the card edge, zoom out the take or reduce the subtitle to 56 px. B-roll from y 230 to 614 at 70 % of the width. In `space.json` this variant is declared with `"card": {"edge": N, "subtitle": "below-face"}`.
   - **Split view inside a to-camera video (layout 1).** The card solves the sections where a graphic does not fit next to the face at a legible size. From top to bottom: the large graphic, the subtitle at the seam (vertically centered between the bottom edge of the graphic and the top of the hair, with the same space above and below) and the card with the room, whose edge passes at eyebrow height, so the hair and the whole forehead stick out (the creator's cutout, aligned pixel by pixel with the take, is only seen above the edge). There is a single edge for the whole piece, below the graphic and the subtitle with space down to the hair, and it is set according to the head, never according to the top edge of the take: each section shifts its take vertically until its eyebrows are at the height of the edge. Above the edge nothing of the take is seen except the cut-out head; a take that starts behind the graphic is an error. Use the take without zoom (full frame of the source) or with a slight zoom, within the framing limit set at ingest. Card corners with radius 140 and the same diffuse shadow as the construction. The space map checks it with the `card.edge` field of each section. If the piece ends with a closing gesture the brand guide defines, the card grows to full screen in about 0.3 s while the gesture starts, so it fills the whole frame before the cut.
   - **Three alternating modes.** *Split* (the longest): b-roll on top, card below. *Graphic only*: the card leaves, the graphic moves down to the center and grows, subtitle below the graphic, in the standard position; for the strong fact or image of each block. *Full camera*: the take at full frame with a punch-in, focus brackets from `brand-guide/assets/icons/` in the corners and a classification pill ("Opinion", "Tip") at the top left; subtitle below the face, in the standard position; for the twist, the advice and the closing, when the creator speaks directly. Mode changes with the motion curves (card that drops and leaves in 300 to 400 ms, graphic that repositions in 400 to 500 ms) and their transition sound.
   - **Color and graphics.** The glow behind the graphic follows the narrative: the mid tone for the neutral, the accent for the twist, the solution or the fact that matters; the key word of the subtitle follows the same color. A single graphic language: every graphic sits in the same kind of window or card with brand chrome (for example a bar with three dots, a title and a status label at the top right). Real sources (a headline, a document, a product page) enter framed in the same window with the relevant sentence underlined: showing the source is also b-roll. Each graphic illustrates the line being said at that second, with 36 px minimum text.

3. **Full-frame scenes (visual video).** The piece has no camera footage: one scene at a time fills the canvas over a backdrop that lasts the whole piece, each scene with one lead visual that acts once and the text that goes with it. `visual-video.md` describes the scenes, their transitions and the base template.

Base rules:

- Closed system: the display font for headlines and figures, the text font for subtitles, pills and labels; brand palette; text sizes only from the scale in "Typography and scale", one value per role in each piece; same margins throughout the piece.
- At most two simultaneous graphic elements besides the creator. Animated subtitle and animated key term never at the same time.
- Every cut, zoom, b-roll and effect exists because it changes the information. If its function cannot be named, it is removed.
- Sections of the creator to camera without graphics are part of the design.

## Canvas and zones

- 1080x1920. Safe zone for essential content: full width, with a 60 px composition margin on each side (x 60 to 1020), and from y 210 to 1680. These are Instagram's organic figures, verified on 2026-11-03 against the app's home feed, profile post view and Reels viewer: the video always enters at full width and is only cropped top and bottom (up to 90 px per side in the home feed); above y 210 fall the status bar, the Reels viewer icons and the feed's user row; below 1680 is outside the profile grid, which shows the 3:4 center (y 240 to 1680). Meta's ads guide (14 % top, 35 % bottom, 6 % sides) is stricter because it includes the ads interface; it does not apply to organic.
- Button column on the right (Reels viewer): nothing essential at x 945 to 1080 between y 1095 and 1850.
- Subtitles: the box never ends below y 1400 (that is how high the user block, caption and interest buttons of the Reels viewer rise in their highest state). Position in "Subtitles".
- No logo as a signature or a corner mark: it takes up useful height and the platform already shows whose video it is. It stays in carousels, Stories and covers. The one exception is the faint logo inside the brand background ("Showpiece effects"), when the brand has one and its guide allows it. The top left corner is for the classification pill and the beat headline; the right, free for the visuals.

## Typography and scale

| Role | Font | Size | Color |
|---|---|---|---|
| Giant typography | Display font, bold | 380 to 440 px, letter spacing -12 px | Accent; white second line at 120 px |
| Beat headline | Display font, bold | 96 to 118 px, line height 1.02 | White with one word in the accent; flat dark background shadow 6 px |
| Subtitle | Text font 700 | 64 px, line height 1.1 (at 80 px they look big) | White; key word in the accent; dark background box at 80 % with radius 24 and padding 18 x 38 |
| Pill and label | Text font 700 (kicker and label) or 600 (button) | 36 px minimum (56 px if it is the only piece of text); no on-screen text below 36 px | The on-accent color on the accent, or white with a white border |
| Lines of code or data (optional, in a window) | Monospace | 36 to 40 px, line height 1.5 | Light neutral on the window background; active line with accent background at 18 % and accent left bar; the rest at 45 % |

## Legibility and composition

The same rules as static social graphics. In video the text is read in motion and for a few seconds, so the scale already starts larger.

- **36 px minimum** for any text on the 1080 canvas: labels, job titles, code and the text inside screenshots. If a screenshot does not reach 36 px with zoom, crop it more or replace it with a card with the fact.
- **Supporting text does not look tiny or compete with its headline.** Next to giant typography, the second line goes at 120 px; next to a beat headline, the punchline goes at 56 to 64 px; a pill alone on screen, at 56 px.
- **Watch the weight of the accent on screen.** If several accent elements coincide (beat headline word, subtitle key word, pill) and none stands out, remove one (the subtitle word in white or the pill with a white border). It is decided case by case, it is not a fixed rule: when in doubt, show the user the piece with and without the change.
- **Balanced lines:** no single word alone on the last line of a beat headline or a punchline. Force the break if needed.
- **No shape or graphic element touches a text:** stickers, arrows, pills and edges of floating screenshots leave visible space around the headline and the subtitle.
- **Text can cross the creator's body or an object** (shoulder, hand, what they hold) if it looks good and reads completely. If the crossing gets in the way of reading or looks forced, move the headline or reframe. The face is never covered.
- **No dead space in cards and brand backgrounds:** if a block leaves a third of the canvas empty, center it vertically, enlarge the image or add a supporting line. Does not apply to sections of the creator to camera without graphics, which are left open on purpose.

## Subtitles

- **One line, below the face.** The default while the creator is on camera: a subtitle is a block of 2 to 4 words on a single line of up to 24 characters at 64 px, appearing whole, below the face with at least 40 px of visible space under the chin. Never a one-word block: if one is left alone, it is balanced with the previous block. A block that does not fit on one line becomes two blocks.
- **Position.** The box (about 106 px tall) sits with its bottom edge between y 1290 and 1400; the default is y 1390, the lowest position, which leaves the most space under the chin (`bottom:530px` in the recipe). It is raised within that range only when something essential sits behind it. The only planned exception is split view variant 2a, where it sits at the seam above the head. If a framing leaves the chin so low that the subtitle does not fit below it (a very close shot), explain it to the user in the proposal or in the visual test and propose the way out (reframe, lower the punch-in or raise the subtitle only in that section); never put it over the face without the user's go-ahead.
- The block's key word in the accent, fixed from when it appears; never word-by-word animation or karaoke.
- Entry 100 to 150 ms with fade and 8 px rise; exit 100 ms. No bounce, no scale.
- Centered; semi-transparent dark background box. If the box covers something important, a 3 to 4 px outline instead of a box.
- Reading ceiling: 17 characters per second by default, a conservative value that is configurable per language (the brand guide or a published reference for the language sets another; `verify-scenes.py` takes it with `--cps`), for text the viewer has to read without the support of the voice (headlines, lists). Subtitles follow speech even if the creator speaks faster: then blocks of 3 to 4 words; each block lasts as long as its words, minimum 0.5 s.
- Always burned in, no emojis and no all-caps text; human review of names and figures. When publishing, also turn on the app's automatic captions.

## Headlines, pills and text

All on-screen text is written in the language of the piece; the labels below are given in English as examples.

- **Text that does not repeat the voice.** The subtitles already say what the creator says. A headline, pill, list or label only goes in if it adds something the voice does not say: a figure that has to stick (the giant typography of the hook), a credential, a date, a fact or a visual joke. No headline per beat and no lists that transcribe the spoken enumeration; in a 45 s piece, about four texts besides the subtitles is normal: a headline in every frame saturates the screen and competes with the subtitles. As an exception, key phrases said by the creator are highlighted with animated typography: one every 20 to 25 seconds of video, that is, two or three in a one-minute Reel (the hook's, the central idea to remember and, if it deserves it, the punchline) and proportionally more in a long video. While a key phrase is on screen, that line's subtitle does not appear. Never a headline per beat.
- **The creator's credential** (who they are, in the words of `brand-guide/positioning.md`): at most once per piece, in the first to-camera section after the hook, as a one-line accent pill near the face that enters with the line and leaves once it has been read. It is placed and checked with the space map like any other graphic.
- **Beat headline:** 2 to 6 words, names the idea, does not transcribe the line. Left-aligned at x 108, with its top edge between y 240 and 340. It enters a few frames before the word that motivates it and stays while the idea lasts, at least the time it takes to read it twice.
- **Classification pills:** "Fact", "Opinion", "Inference", "Step N", "Tool". One at a time, top left corner (x 108, y 240), aligned with the beat headline, which starts below it (around y 340) when there is a pill. Used when the script separates fact and opinion and in lists of steps.
- **Pinned term:** white pill with a border for a technical term, a word in another language or a proper name; lives 10 to 20 s; at most one at a time.
- **List that builds:** each item enters as it is said; the previous ones drop to 60 % opacity.
- **Animated figure:** a 0.5 to 1 s counter with tabular figures and no line break, so it does not change width or lines while counting; at most one per video, only with a verified figure.
- **Animated underline:** a 4 to 8 px stroke drawn in 8 to 12 frames under the key word of a headline; once per block.
- **Quote:** full sentence plus name and job title in a smaller size; only with a source.
- **Humor label (optional).** When the brand's voice guide (`brand-guide/voice-and-humor.md`) uses humor, a short pill in the creator's voice can point at a funny detail of the creator's own footage. A brand without humor in its guide does not use it.

## B-roll and screen

- It enters at the second the line names what it shows; lasts 3 to 5 s per clip or per block (in event recaps, shots of 0.7 to 1.5 s grouped in a 3 to 5 s block; below about 0.7 s the shot is not perceived: if they do not fit, remove a shot and spread its time among the others, instead of shortening them); L cut on entry and J cut on exit with the creator's audio continuous.
- Mandatory function from a closed list: illustrate, show the demo, compare, establish the location, cover a cut with the same idea.
- Modes: full screen; floating screenshot (80 to 90 % width, radius 16 to 24, shadow blur 40 to 60 at 25 %, enters with scale 96 to 100 % in 300 ms); picture in picture (the creator in a window of 25 to 35 % of the width, bottom left of the safe zone, radius 16 to 24); split screen only for before and after with large elements.
- Screenshots: zoom into the relevant region until the text is at 36 px or more on the canvas (if it does not get there, crop more or replace with a card with the fact); screenshots at 2x; never the whole desktop cropped. In pieces that show code, commands or data in lines, they go in their own window with 8 to 10 visible lines and the line being discussed highlighted.
- Neutral device mockup, without third-party logos.

## Generated scenes

Screens, chats, documents, objects or data that are built instead of recorded: a tool's interface, a chat, a demo, a figure. They use the same system (typography, palette, zones and motion) and add what is specific to a built scene.

- **Truth before effect.** What appears exists and behaves as in reality: names, states, flows and capabilities. If the script asks for something the tool does not do, the script changes. Every on-screen text is literally true; when in doubt, claim less.
- **Demo data.** In a recreated interface, the data (people, amounts, dates) is fictional, consistent across scenes and reads as an example, never as real results of the creator, a client or a product. Real or personal data is not hidden with blur: it is replaced before capturing. No third-party brand, logo or name that there is no right to show.
- **Recreate, do not paste.** A screenshot is a reference. What the scene needs is rebuilt in HTML, at video scale and with the brand identity, showing the leading element and not the whole screen, with its real structure and names. From the original, only what cannot be faithfully recreated (a photo, for example) is reused, in a clean version.
- **Understood without explanation.** Every scene has an object that is recognized instantly and keeps its proportions and conventions (a phone still looks like a phone); if it needs a caption, the object is badly chosen. The story is told inside the object, with its own resources (a message that arrives, a state that changes), not with loose elements around it. One idea per scene: if there are two, they are two scenes.
- **Depth without losing legibility.** Space comes from layers, entries from the background and camera movement, not from rotating what has to be read. Changes happen in place and in view; the data is never hidden to achieve an effect. Between scenes, the transition is a camera move, a depth move or an object that turns into another, not a generic fade.
- **Composition.** One lead per shot; the secondary is subdued with blur, darkening or scale. With the creator in frame, the lead is the creator and the scene occupies the free space without covering them. Cards and panels with height fitted to their content and the same inner margin throughout the piece. Between a text and the object, at least 65 px, also during animations.
- **Reference screenshots.** Request them with fictional data consistent across screens, and with the name or logo hidden if the piece must not show them: desktop at 1280 x 800 and mobile at 390 x 844, with scale factor 3. To recreate a change, pairs of state A and B with the same framing, scroll and size. If there are elements to animate or crop, a JSON next to each image with `viewport`, `deviceScaleFactor` and their boxes `{x, y, width, height}` in CSS px. They are saved in the piece's `source/broll/` (or in `media/broll/<topic>/` if they serve several pieces) as lossless WebP (`cwebp -lossless -z 9 -metadata none`, checking that the pixels match the original), with a `catalog.md` that states per file the device, what it shows and what must not be shown (absurd figures in the demo data, cut-off sections).

## Showpiece effects

1. **Brand background behind the creator cut out.** When the background is context b-roll, always a video, never a photo. The dark background with the brand texture, if the brand has one (from `brand-guide/assets/textures/`; if it is a small raster, scale it with a soft 2 to 4 px blur so the pixelation does not show), moving about 20 px per second; behind, optionally, the brand's logo large at 7 % opacity (the only logo a video carries, and only if the brand guide allows it); beat headline at the top. Per-frame cutout with `hyperframes remove-background`. Two or three sections per piece: hook, strong headline, context b-roll behind. Check the fine edges of the cutout in the first render (hair, accessories and hands); if the edge does not pass, replace with a floating screenshot. Never with text to read behind.
2. **Giant typography.** A figure or word at full screen over the image darkened to 78 %, 1 to 2 s, entry with fade and scale from 96 to 100 % in 400 ms, exit in 200 ms. One per video.
3. **Dynamic zoom into the screen.** The virtual camera goes in from the creator to the window or screenshot and back. Target scale = (1080 minus 2 margins of 12 px) divided by the window width, so the window fills the width and the text is never cut. Zoom origin at the center of the window. In 700 ms and back 600 ms with a smooth ease-in-out curve; whoosh going in and coming back. Once or twice per piece, in demos.
4. **Parallax and depth.** Card with perspective (1800 px) and layers at different depths; rotation of about -18 to -5 degrees over 3 to 4 s with continuous linear motion, with no change of speed after the entry (a curve change midway looks like a jump). The layers start from their initial position set at second 0. Only over static screenshots longer than 4 s.

## Punch-ins, zooms and sounds

- Two shot sizes from the same take, 100 % and a punch-in, alternated; the change falls on a change of idea. Never two consecutive cuts at the same size. The punch-in goes up to the scale the master was built for (120 % with the default master, up to 200 % with a 4K original); with a 1080x1920 original it is limited to 110 to 115 % ("Framing" in `SKILL.md`).
- Animated zoom with intent: 1.0 to 1.18 in 120 ms with a strong ease-out curve, on the emphasis word; back in 400 ms.
- Sound on every camera change, with the system sounds of `find-video-audio/references/sound-catalog.md` ("System sounds": each role is a fixed file chosen by the user and noted in its row of `media/audio/inventory.md`). Every punch-in and every shot cut carries a cut hit, a short whip of medium-dark tone (240 ms, at least 10 dB below the voice in any word it overlaps), alternating its variants A and B so it does not sound mechanical. The emphasis zoom carries a more present low hit: the main emphasis hit (it may carry the brand's sound motif blended into the low end) on hook, twist, payoff or reveal, placed 0.2 s before the word when it has a rise; the dry emphasis hit, short and without a tail, when the line continues right away. The entry of a headline or a card, the entrance whoosh; its exit, the exit whoosh, shorter and about 4 dB lower. The block transition, the block transition riser, with its landing (noted in `log.md`) on the moment the new block settles. Budget: cut hits are the sound signature and do not count; on top of them, three to six featured sounds per piece. If the map asks for more, silence first pills, exits and list items from the fourth on.
- Transitions with an effect: two or three per piece (dynamic zoom, wipe with a recorded object, recorded whip pan). Forbidden: cross dissolve between takes of the same phrase, glitch, flash transitions and stock transition packs.

## Motion

The character and criteria of motion (including when to use physical effects such as drops, shake or dust) are in `brand-guide/motion.md`; this section sets the default numbers, which the brand's motion guide can override.

- Entries with emphasized deceleration, cubic-bezier(0.05, 0.7, 0.1, 1.0) or `power3.out`: text and pills 300 to 400 ms; cards and screenshots 400 to 500 ms; full screen up to 800 ms. Never more than 1000 ms.
- Exits with acceleration, cubic-bezier(0.3, 0.0, 0.8, 0.15) or `power2.in`: 150 to 250 ms, always shorter than their entry.
- Nothing linear except continuous drifts (texture drift, progress bars, parallax drift).
- Bounce or overshoot only on the main element of a scene, small, and never on subtitles.
- Elements of the same group enter with the same curve and a stagger of 40 to 80 ms.
- Between two main texts, the one leaving finishes before the next enters (maximum overlap 0.1 s). Never two main texts at once or two states of the same object visible at once.
- A key phrase can transform into something else (for example, into a header) instead of leaving: 450 to 600 ms, smooth curve at both ends (`power3.inOut`), in a single gesture. After scaling it stays at 36 px or more.
- State changes (a check, a button that activates, a message that arrives): 150 to 350 ms, like a short pulse. The important change happens where it is best seen, not where it happened to end up.
- Shakes and camera hits: a few frames, and they return exactly to their position.
- The brand texture, if the brand has one, only as background for cards and the brand background, subtle, with a slow drift.
- Icons, stickers and glyphs (arrows, focus brackets, illustrated stickers) only from `brand-guide/assets/icons/`, never hand-drawn. A one-ink glyph can be white or a palette color; illustrated stickers keep their colors. One or two per piece at most, following the icon rules of `visual-identity.md`. Use them only where the system already calls for a graphic (the arrow of a label, focus brackets over a screenshot); a new use is proposed to the user in the edit proposal.

## Sound

- Voice: moderate cleanup only when needed, and normalization to -14 LUFS integrated (acceptable range -16 to -14) with a true peak target of -1.5 dBTP, so the encoded file stays at or below -1 dBTP. Phone recordings often arrive with clipped peaks: normalization is mandatory ("Voice level" in the recipes; `scripts/loudness.sh` measures it). The finished mix gets the same target in the final encode.
- SFX: cut hits on every shot change plus three to six featured sounds per piece, synced to the frame of the movement, with a low, soft character. In any word it overlaps, an effect stays at least 6 dB below the voice and a cut hit at least 10 dB (`scripts/verify-sfx.py`).
- Music: only free or generated locally. 20 dB below the voice with ducking (drops 6 to 12 dB when the voice enters, recovers slowly), rises in voice gaps, no lyrics, no high BPM. Absent in dense explanations, sensitive topics or when the ambience adds something. In a sketch, music that cuts dead as a punchline.
- Human rhythm: a repeated action (typing, clicks, notifications) varies intervals and samples; at equal intervals it sounds mechanical.
- One sound per movement. If a movement is visual and semantic at once (a card that enters and is a confirmed payment), the semantic sound wins.
- Room tone in the gaps; digital silence never.

## Color

- Everything in Rec. 709 SDR. HDR clips from a phone (HLG or Dolby Vision): render with `--sdr` and ask the user that the next recording be made with HDR video turned off in the camera settings, and in 4K when possible.
- Consistent skin across shots; restrained saturation; third-party b-roll is matched to the main take.

## Opening and closing

- **Live hook, never still.** In the first seconds (the hook line) something moves besides the creator: a hook where only the text changes looks flat. By default there are no subtitles on it; the hook text is the animated typography, synced word by word with the voice. It carries three things:
  - **Camera:** a slow continuous push-in and one or two zoom hits with sound, on the word that hooks and, if there is one, on the punchline. Never one hit per word: three zooms with sound in four seconds sound mechanical, and those hits count within the three to six featured sounds of the piece.
  - **Visual world from frame 0:** if the piece has its own world (the objects that later star in the video), it is on screen from frame 0 in layers at different depths behind the creator cut out, drifting slowly and linearly (`brand-guide/motion.md`) and reacting to the line. If it does not have one (opinion, event, commentary), the topic's b-roll darkened with the dark background color, without the background appearing abruptly. These background layers do not count toward the maximum of two graphic elements; the drift stays slow so the eye goes to the word and to the creator's face.
  - **Hierarchy in the text:** the word that hooks enters at double size, in the accent and with a scale hit (a figure counts up to its value with a low hit). The rest goes in short lines, each on its own dark background pill, never a band that covers the gesture.

  The hook ends with an action that leads to the next shot: the objects leave toward where they reappear. In a series with an intro, that exit leads into the intro, which stays as defined. Subtitles start with the second line. Exception: in a humor sketch a still, deadpan hook can be the joke itself; it is decided and stated in the proposal.

- By default, no logo, card or presentation before the hook. The first frame is the one `recommend-video-hook` decided; the hook text enters at frame 0.
- **Intro only if the series defines it.** A standalone piece has no intro. Whether the intro exists is decided once per series, when designing it with the user, and stays in its plan (`editorial/series/<series>/series.md`). If the plan defines an intro, every episode carries it, right after the hook and never before, exactly as defined (text, animation and duration), brief (about 4 to 7 s at the final pace) and without redesigning it per episode. If the plan does not define it, no episode carries it.
- By default the video ends on the payoff and the one call to action that follows it, with a hard cut: no outro, closing card or graphic signature, unless the brand guide defines one.

## Per-format adjustments

The formats below are the usual ones, not a closed list; a piece that fits none takes the full system of the educational format and states its differences in the proposal.

- **Educational:** the full system; a visual change with a function every 5 to 10 s, denser in the first 6 s.
- **Demo:** picture in picture, dynamic zoom, a window with the screen or the steps, arrows and highlights over the screenshot, steps with pills.
- **Opinion:** fewer graphics, more of the creator; "Fact" and "Opinion" pills; a quote if there is one; minimal music or none.
- **Progress update** (one episode of work shown as it advances, for example a build-in-public series, a challenge or a renovation diary): a real figure on screen, the real state of the work as the first frame, a "Day N" label.
- **Community or event (recap):** the creator to camera in hook and closing, the creator's own b-roll in blocks with short shots, one figure in giant typography at most, music somewhat more present (16 to 18 dB below the voice) and muted in to-camera sections if it gets in the way.
- **Sketch:** comic timing rules; hold the shot when the silence is the joke; reaction zoom and quick cut to the reaction; music that cuts abruptly; sober subtitles; no beat headlines; meme sounds allowed.

- **Visual video** (no camera take, with voice-over or without voice): layout 3, usually 15 to 45 s. Its scenes, text, timing, subtitles and sound are in `visual-video.md`; the typography, zones, motion and sound numbers of this file apply to it unchanged.

The humor label of "Headlines, pills and text" fits the recap and the sketch when the brand's voice guide uses humor.
