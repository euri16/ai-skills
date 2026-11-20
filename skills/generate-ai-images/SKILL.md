---
name: generate-ai-images
description: Generate or edit AI images for a content piece when what is needed does not exist in the real material. Three modes. Edit a real photo of the creator changing only what was asked (a gesture, a pose, an object) without touching their identity. Create effects and elements to composite (explosions, sparks, smoke, confetti, objects, textures) on a plain background, ready to blend or cut out. Create general images (backgrounds, scenes, objects, illustrations), with fictional people only when the piece needs them. Use when the user asks to "do it with AI", to recreate a photo with a different gesture, to generate an explosion, smoke or a background, for an image that cannot be photographed, or when another skill (design-reel-cover, edit-short-video or a social graphics skill) needs an image the material does not have. Does not generate the creator's face from scratch, nor real people, nor anything that passes itself off as real.
---

# Generate AI Images

AI solves what the camera did not capture: a gesture that never made it into a take, an explosion that cannot be filmed in a room, a background for a scene. The risk is that the image stops being honest: a face that is no longer the creator's, an effect that looks like something else, an invented person presented as real. This skill generates little, starting from the real material whenever it exists, compares every result with the original and uses nothing without the approval of the user.

The creator is the person who appears in the videos and photos; the user is who decides and approves. The workspace layout (`social/<piece>/`, `piece.md`, `brand-guide/`) is described in the repo's `CONVENTIONS.md`.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| [Codex CLI](https://github.com/openai/codex) (`codex`), signed in, with its image generation tool | Yes | Every generation and edit: `scripts/generate.sh` runs `codex exec` | `npm install -g @openai/codex`, then `codex login`. `command -v codex` checks the install; the image tool can only be checked by generating: if the first run ends with "MISSING" and its log says Codex has no image tool, stop and tell the user |
| `uv` | No | Running `scripts/compare-face.py` (numpy, opencv-python-headless, pillow) in a temporary environment. Without it, mode 1 is skipped: no edited photo of the creator is shown without this face check | `brew install uv` or `pip install uv` (other installers at https://docs.astral.sh/uv/) |
| `python3` with Pillow | Yes | `scripts/side-by-side.py`, which builds the sheet every result is presented on; it also prints the size of each output in `generate.sh` | `python3 -m pip install --user Pillow` |
| `ffmpeg` | No | Reducing the base photo before attaching it. Without it, on macOS, `sips -Z 2048 <copy>` does the same | `brew install ffmpeg`; on Linux, `sudo apt install ffmpeg` |
| `brand-guide/visual-identity.md` | No | The palette colors named in the prompts of modes 2 and 3 | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/visual-identity.md` there is a filled-in example |
| The piece folder `social/<YYYY-MM-DD-slug>/` with its `piece.md` | No | Where working images go (`<destination>/generated/`) and where every generated image that is used is recorded, with `- AI: yes` in its header. Without it, ask the caller where the images go and tell them the piece must be flagged as AI-generated | Create it as described in "A piece folder" of `CONVENTIONS.md` in the ai-skills repo |
| Skill `analyze-video` | No | Its gesture search (`analyze-video/references/find-gesture.md`), to look for a gesture in the takes before editing a photo with AI | Install the `analyze-video` skill from the ai-skills repo next to this one |
| Skill `design-reel-cover` and `uv` | No | Its `design-reel-cover/scripts/cutout.py` with `--model isnet-general-use` (cutting out opaque elements; the default model of that script is for people) and `design-reel-cover/scripts/preview.sh` (checking an effect in the grid view). Without it, opaque elements are delivered on their plain background | Install the `design-reel-cover` skill from the ai-skills repo next to this one |

## Modes

| Mode | What it does | Base |
|---|---|---|
| 1. Edit a real photo of the creator | Changes only what was asked (a gesture, a pose, an object, clothes) and keeps everything else identical | A real photo or frame from the piece; optionally, a crop from another take as reference for the gesture |
| 2. Effects and elements to composite | Explosion, sparks, smoke, confetti, an object or a texture, isolated to blend into a cover, a graphic or a video | None. The background depends on the element: pure black for what emits light or is light and translucent, pure white for dark smoke, a plain contrasting color for an opaque object that will be cut out (`references/prompts.md`) |
| 3. General images | Backgrounds, scenes, objects or illustrations | None, or a style reference |

Each effect is generated to the user's request; there is no fixed effect library. The prompt names the phenomenon with its physical traits so the AI does not confuse it with something else: an explosion goes out in all directions from a central flash; a fan-shaped jet of sparks reads as welding or an angle grinder. Templates in `references/prompts.md`.

## Limits

- The creator's face is never generated from scratch: mode 1 always starts from a real photo of them from the piece.
- Never real people or people resembling someone specific. Fictional people only to illustrate a situation or a concept, never presented as real (client, event attendee, testimonial, review) nor in place of the creator, and sparingly: stock-photo aesthetics weaken a personal brand.
- Never third-party brands or logos, nor anything that passes itself off as real (screenshots, receipts, documents, news).
- Every generated image is presented marked as generated, next to the real one when there is one, and does not go into a piece without approval from the user.
- Every generated image that is used is noted in the piece's `piece.md`, and the record's header carries `- AI: yes`, the field `schedule-social-piece` reads to flag the content as AI-generated on the platforms.

## Flow

Commands are run from the workspace root; `<skills>` is the folder where these skills are installed and `<work>` the piece's `<destination>/generated/` folder.

1. **Define.** What is needed, in which mode and where it will be used (cover, graphic, video; size and crop). In mode 1, choose the base photo with the user: if the requested gesture exists in some take, look for it first with the gesture search of the `analyze-video` skill (`analyze-video/references/find-gesture.md`); AI is for what the material does not have.
2. **Prepare.** Working images go in the piece folder (`social/<piece>/<destination>/generated/`, for example `cover-src/generated/`): a copy of the base with its long side at 2048 px at most and, if needed, a reference crop of the gesture or the style. The original is never touched.
   ```bash
   ffmpeg -y -i <original> -vf "scale='min(2048,iw)':'min(2048,ih)':force_original_aspect_ratio=decrease" <work>/base.png
   ```
3. **Generate** with a prompt (`<work>/prompt.txt`) written from the templates in `references/prompts.md`: in mode 1, "keep everything identical and change only X"; in all modes, two versions when the variation helps decide, and the output file names.
   ```bash
   <skills>/generate-ai-images/scripts/generate.sh <work> <work>/prompt.txt a.png b.png -- base.png
   ```
   If a result does not meet the request (for example, the change that was asked for is barely visible), regenerate only that one with a more specific prompt before showing anything.
4. **Verify** before showing:
   - Mode 1: measure the difference in the face area against the exact base that was attached, and get the side-by-side crop of both faces:
     ```bash
     uv run -q --python 3.11 --with numpy --with "opencv-python-headless<5" --with pillow python <skills>/generate-ai-images/scripts/compare-face.py <work>/base.png <work>/a.png <work>/a-face.png
     ```
     Look at the crop at full size (features, skin, hair, accessories, expression) and check hands (five fingers, jewelry, proportion), clothes and background in the full image. Discard any version that changes the identity. The script stops when the generated image has other proportions than the base: regenerate asking for the same aspect ratio.
   - Modes 2 and 3: it looks real (or in the requested style), with no text, brands, deformations or background edges; the effect is the requested phenomenon.
5. **Present** the versions side by side in a single image, next to the real photo when there is one, each under a label that says which one is real and which ones are generated:
   ```bash
   python3 <skills>/generate-ai-images/scripts/side-by-side.py <work>/versions.png "<Real photo>" <work>/base.png "<A · generated>" <work>/a.png "<B · generated>" <work>/b.png
   ```
   Open it for the user (on macOS, `open`). Recommend one and ask with the structured question tool of the agent in use (for example `AskUserQuestion`).
6. **Iterate** with what the user asks for: a new reference (a photo they share), a stronger or subtler version of the change, another intensity. Every round repeats the verification.
7. **Composite and record.** To blend an effect or an element, follow `references/compose-effects.md`. The approved originals are kept in the piece's `generated/`; what is discarded goes to the system Trash, not deleted (`trash <file>` on macOS 15 or later, `gio trash <file>` on Linux; otherwise ask the user to remove it). In the piece's `piece.md`, set `- AI: yes` in the header and note which image is generated, which real photo it starts from and the approval date.

## Resources

| File | What for |
|---|---|
| `scripts/generate.sh` | Runs the generation with Codex (`codex exec`), passing the prompt through standard input and the images as attachments, and checks that the requested files were produced |
| `scripts/compare-face.py` | Detects the face in the real photo, measures the difference with the generated one in that area and leaves the side-by-side crop of both faces |
| `scripts/side-by-side.py` | Joins the real photo and the versions into one labeled sheet to present them |
| `references/prompts.md` | Prompt templates per mode and how to describe effects |
| `references/compose-effects.md` | Blending an effect or placing a cut-out element over a photo or a video: blend mode, point of origin, mask so it does not cover the face |

## Rules

- Everything delivered (chat, questions, labels, notes in `piece.md`) goes in the user's language, or the one the workspace instructions set; the prompt to the AI can be in English.
- This skill publishes nothing; whoever invokes it decides the use with the approval of the user.
