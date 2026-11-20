# AI Skills

Reusable [Agent Skills](https://agentskills.io) for building with AI beyond code. Each skill is a folder with a `SKILL.md` that any agent with skills support can load.

There are two sets:

- **Video editing assistant:** turns an agent into an assistant for short vertical videos (Reels, TikTok, Shorts, LinkedIn), from research and script to the edited MP4, its cover, its caption and its schedule.
- **Orchestrator pattern:** keeps a project's knowledge on disk so every new session starts knowing how the work is done, and keeps those documents true with two rules.

## Video editing assistant

The agent can't watch a video or hear a sound. These skills give it eyes and ears with local tools (a transcript with word timings, contact sheets of frames, measured audio levels), let scripts do the heavy lifting, and stop at every decision that needs taste so a human approves it.

| Stage | Skill | What it does |
|---|---|---|
| Research | [`research-content-topic`](skills/research-content-topic) | Turns an idea into a thesis, an angle and verified claims |
| Script | [`recommend-video-hook`](skills/recommend-video-hook) | Writes 12 to 15 hooks with proven templates, scores them, recommends one |
| Script | [`write-short-video-script`](skills/write-short-video-script) | Plan approved first, then the script and its beat map, for a talking head or a visual video |
| Footage | [`analyze-video`](skills/analyze-video) | Local transcription, cut detection, contact sheets and a page to choose the best take of each sentence |
| Edit | [`edit-short-video`](skills/edit-short-video) | Edits a talking-head recording or builds a visual video with no camera take: proposal in text, HyperFrames composition, render and quality control |
| B-roll | [`generate-ai-images`](skills/generate-ai-images) | Generates the images the footage does not have, with Codex |
| Sound | [`find-video-audio`](skills/find-video-audio) | Music and SFX with known licenses (CC0 and CC BY) and a page to choose them by ear |
| Cover | [`design-reel-cover`](skills/design-reel-cover) | Reel cover from the recorded material, checked in the profile grid |
| Caption | [`write-caption`](skills/write-caption) | Caption per platform: first line that hooks and is searchable |
| Schedule | [`schedule-social-piece`](skills/schedule-social-piece) | Schedules the approved piece in Buffer |
| Schedule | [`buffer-api`](skills/buffer-api) | CLI over Buffer's GraphQL API |

Each skill works on its own and invokes the others when it needs them. They expect a workspace with the creator's brand and pieces, described in [`CONVENTIONS.md`](CONVENTIONS.md); [`examples/crumb-theory/`](examples/crumb-theory) is a filled-in profile of a fictional brand to copy and rewrite.

## Orchestrator pattern

An agent forgets everything between sessions. This set puts the project's process and domain knowledge in small documents on disk (a map at the root, a README per folder, skills, state files), turns every correction into a lasting change the user approves, and moves the exact rules to scripts. The guide explains the pattern and how to start in five steps: [English](docs/orchestrator-pattern.md), [Español](docs/orchestrator-pattern.es.md).

| Skill | What it does |
|---|---|
| [`create-agents-map`](skills/create-agents-map) | Interviews you and writes the root `AGENTS.md` with the two rules; optionally a README per folder |
| [`capture-lesson`](skills/capture-lesson) | Turns a correction into an exact change in the right document, written after your approval |
| [`turn-task-into-skill`](skills/turn-task-into-skill) | Packages a repeated task as a minimal skill or an orchestrator with a state file |
| [`promote-rule-to-script`](skills/promote-rule-to-script) | Finds exact, repeated rules and proposes a script or a hook for each |
| [`review-stale-docs`](skills/review-stale-docs) | Compares documents and skills with the code, applies "the code wins" and proposes fixes and retirements |

## Install

Copy the folders you want from `skills/` into your agent's skills folder (for example `.claude/skills/` or `.agents/skills/` in your workspace), or use a skills installer that supports GitHub repos. Install the skills of a set side by side in the same folder: they call each other's scripts by sibling path.

For the video set, also copy [`CONVENTIONS.md`](CONVENTIONS.md) into your workspace. The skills refer to it for the layout they expect, and their setup messages point to it and to the example brand in this repo.

When a skill is invoked, its "Prerequisites" section checks what it needs from your project (brand files, tools, keys) and tells you what is missing and how to set it up before doing anything.

## Requirements

| Tool | Used by |
|---|---|
| ffmpeg and ffprobe | analyze-video, edit-short-video, find-video-audio, design-reel-cover, schedule-social-piece |
| curl and Python 3 with numpy | find-video-audio |
| cwebp (optional) | design-reel-cover, edit-short-video |
| macOS on Apple Silicon | analyze-video (local transcription), edit-short-video (through analyze-video; not needed for a visual video without voice) |
| Google Chrome | analyze-video, design-reel-cover (rendering pages to images), edit-short-video (through analyze-video; HyperFrames downloads its own headless Chrome) |
| [Vercel CLI](https://vercel.com/docs/cli) | buffer-api, schedule-social-piece (uploading local media) |
| Python 3.11+ and [uv](https://docs.astral.sh/uv/) | video scripts with dependencies (Whisper, OpenCV, rembg, Pillow) |
| Python 3.7+ | review-stale-docs (`check-docs.py`, standard library only) |
| Node.js 18+ (22+ for HyperFrames) | buffer-api, schedule-social-piece, HyperFrames |
| [HyperFrames](https://github.com/heygen-com/hyperframes) and its skills | edit-short-video (rendering) |
| [Codex CLI](https://github.com/openai/codex) | generate-ai-images |

The rest of the orchestrator set needs nothing else: it works with Markdown files.

### Environment variables

| Variable | Skill | Required |
|---|---|---|
| `BUFFER_API_KEY` | buffer-api, schedule-social-piece | Yes, to talk to Buffer |
| `BUFFER_TIMEZONE` | buffer-api, schedule-social-piece | To schedule (or `- Time zone:` in `piece.md`) |
| `BLOB_READ_WRITE_TOKEN` | buffer-api, schedule-social-piece | To upload local media to Vercel Blob |
| `FREESOUND_API_KEY` | find-video-audio | To search Freesound (its API terms cover non-commercial use) |
| `WHISPER_VOCABULARY`, `WHISPER_LANGUAGE`, `VOICE_PITCH_RANGE` | analyze-video | No: names and terms for the transcription, default language, pitch range of the voice |
| `CHROME_BIN` | analyze-video, design-reel-cover | No: browser binary if not at the default macOS path |
| `BUFFER_YOUTUBE_CATEGORY` | buffer-api, schedule-social-piece | For YouTube, unless the piece has `- Category:` |
| `BUFFER_ORGANIZATION`, `BUFFER_QUEUE_LIMIT`, `WORKSPACE_ROOT`, `BUFFER_STATE_DIR`, `BUFFER_SECONDARY_TIMEZONE`, `BUFFER_API_URL` | buffer-api, schedule-social-piece | No |
| `BRAND_DIR`, `CONTACT_SHEET_*`, `COMPARE_*` | analyze-video, design-reel-cover | No: brand overrides |

Each skill's `SKILL.md` lists its variables in its "Prerequisites" section.

## Principles

- **The human approves.** Plans, takes, sounds, edits, covers, captions and changes to the project's rules are proposed and approved before anything is rendered, scheduled or written. Nothing is published without explicit approval.
- **Scripts for the exact work, the model for judgment.** Transcription, measurement, rendering and checks run locally and deterministically; the model reads their output and proposes.
- **No invented facts.** No anecdotes, figures or results the user did not provide or a source does not support.

## License

[Apache License 2.0](LICENSE).
