---
name: schedule-social-piece
description: Schedule in Buffer an already approved piece from `social/<YYYY-MM-DD-slug>/` for Instagram, TikTok and YouTube Shorts, at the time set in its piece record (`piece.md`) and in the time zone configured for it, with the cover stuck on as the first frame on all three channels, and keep the record up to date when Buffer publishes. Use it when the user asks to schedule a piece, book a Reel for a given day and time, upload it to TikTok and Shorts, put it on the calendar, check what already went out or update the piece records with what was published. Depends on `buffer-api`. Does not write captions or titles (that is `write-caption`), does not design covers (`design-reel-cover`) and does not publish instantly.
---

# Schedule social piece

Bridge between the piece records in `social/` and Buffer. Depends on
`buffer-api`: invoke it with the skill tool before starting, to load its
rules (rehearsal, `--check`, approval, `--yes`, verification). The
workspace layout (`social/<YYYY-MM-DD-slug>/`, `piece.md`, `export/`,
`edit/tests/`) is described in the repo's `CONVENTIONS.md`.

Write everything the user reads (chat, questions, plans)
in the user's language, or the one the workspace instructions set. The
field names the script reads and writes in `piece.md` are fixed (English,
listed below).

## Prerequisites

Check these when the skill is invoked, before doing anything else. Check that environment variables are set without printing their values. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| Skill `buffer-api` | Yes | Every Buffer call and the write rules; `scripts/schedule.mjs` imports `../buffer-api/scripts/buffer.mjs` | Install the `buffer-api` skill from the ai-skills repo in the same skills folder as this one |
| The required items of `buffer-api`: Node.js 18 or later, a Buffer account with the channels the piece goes to connected (this skill handles Instagram, TikTok and YouTube), `BUFFER_API_KEY` | Yes | Running the script and talking to Buffer | See Prerequisites in the `buffer-api` skill |
| `BLOB_READ_WRITE_TOKEN` and the `vercel` CLI | Yes | Uploading each video to Vercel Blob, where it gets a public URL until its cleanup: `plan --check` and `run` always send local files | See Prerequisites in the `buffer-api` skill |
| `ffmpeg` and `ffprobe`, with the `libx264` and `aac` encoders | Yes | Reading each video and generating the video with the cover stuck on, re-encoded in H.264 and AAC | `brew install ffmpeg`; on Linux, `sudo apt install ffmpeg` (both builds include the two encoders) |
| The approved piece record `social/<YYYY-MM-DD-slug>/piece.md` and its video in `export/` | Yes | What gets scheduled: caption, time, YouTube title, category and privacy, file (see "What the piece record needs") | Written by the earlier stages (`edit-short-video` exports the video, `write-caption` writes the captions); layout in "A piece folder" of `CONVENTIONS.md` in the ai-skills repo |
| A time zone for each schedule | Yes | Reading `- Schedule:`; which zone wins is in "What the piece record needs". Without one, that channel is blocked | Write `- Time zone: <IANA zone>` in the header of `piece.md`, or `export BUFFER_TIMEZONE=<IANA zone>` |
| A YouTube category for each Short | Yes, for YouTube | Buffer requires a category id to create a YouTube post; without one, that channel is blocked | Write `- Category: <id>` in the YouTube section of `piece.md`, or `export BUFFER_YOUTUBE_CATEGORY=<id>` as the workspace default (see Prerequisites in the `buffer-api` skill) |
| `cover-<channel>.png` or `.jpg` in the piece folder | No | The cover stuck on as the first frames; without it the thumbnail is the video's first frame | Made with the `design-reel-cover` skill |
| `social/index.md` | No | Checking after publishing that the piece has its row | Write it following `CONVENTIONS.md` in the ai-skills repo |
| `BUFFER_QUEUE_LIMIT`, `BUFFER_SECONDARY_TIMEZONE`, `BUFFER_STATE_DIR`, `WORKSPACE_ROOT`, `BUFFER_API_URL`, `BUFFER_ORGANIZATION` | No | As in `buffer-api`; `WORKSPACE_ROOT` (default: the current directory) must contain `social/` | See Prerequisites in the `buffer-api` skill |

## Commands

```bash
schedule() { node <skill-dir>/scripts/schedule.mjs "$@"; }
schedule plan 2026-11-02-example-piece            # rehearsal per channel, generates the video with cover
schedule plan 2026-11-02-example-piece --check    # also validates on the server (temporary drafts)
schedule run 2026-11-02-example-piece --yes       # schedules and records in piece.md
schedule sync --write                              # marks published with link and cleans up the media
```

`--channels instagram,tiktok` limits the channels; `--type post|story`
asks Buffer for another Instagram type (a video is a Reel by default;
validate another type with `plan --check`, since Buffer decides whether it
accepts it); `--force` creates another post even if the section already has
a Buffer id. `schedule cover <piece> [--channel instagram|tiktok|youtube]`
only generates the video with the cover stuck on and its control frame.

## What the piece record needs

One section per channel the piece goes to: `## Instagram`, `## TikTok` and
`## YouTube` (or `## YouTube Shorts`). A channel without a section is
skipped. Each section has:

~~~markdown
## TikTok

- Status: approved
- Schedule: 2026-11-10 19:00
- Link:

Caption:

```
<approved caption>
```
~~~

- Time zone of `Schedule`, first match wins: a zone written in the field
  (`2026-11-10 19:00 (Europe/London)`), `- Time zone: <IANA zone>` in the
  record's header (before the first `##` section), or the
  `BUFFER_TIMEZONE` variable. Without any of them that channel is blocked.
- YouTube also needs `- Title:` (100 characters at most, no `<` or `>`)
  and a category: `- Category: <id>` (the numeric YouTube category id;
  text after it, such as the category name, is ignored), or the
  `BUFFER_YOUTUBE_CATEGORY` variable when the section has none. It accepts
  `- Privacy: public|unlisted|private` (public by default). That section's
  caption is the Short's description.
- `- AI: yes` in the record's header (before the first `##` section) flags
  the content as AI-generated on every channel; written in a channel's
  section, only on that channel. The line counts nowhere else in the
  record.

## What it does

1. Reads each section with `Status: approved`. Skips the channels with no
   section, those that are not approved or that already have
   `- Buffer: <id>`, and blocks if the schedule time, its
   time zone, the caption, the YouTube title or category, or the video is
   missing.
2. Video: `export/<slug>-<channel>.mp4` (`-instagram`, `-tiktok`,
   `-youtube`), if it does not exist `export/<slug>.mp4`, and otherwise the
   only video in `export/`. An `-archive.mp4` copy is only used as a last
   resort, with a warning.
3. On every channel it generates `export/<slug>-<channel>-buffer.mp4`
   (or `<slug>-social-buffer.mp4` if several share video and cover) with
   `cover-<channel>.png|jpg` stuck on as the first 2 frames (about 66 ms at
   30 fps), re-encoded in H.264 CRF 16, with silence under those frames so
   the audio stays in sync. TikTok and YouTube use `cover-instagram` if
   they do not have their own. The control frame is left in
   `edit/tests/buffer-<channel>-frame0.jpg` (`buffer-social-frame0.jpg`
   for the shared file). Without a cover, the thumbnail is the video's
   first frame.
4. Rehearses `buffer post create` per channel with `--thumb-offset 0`: local
   time with its zone, UTC and the optional secondary zone, the channel's
   scheduled posts (against `BUFFER_QUEUE_LIMIT` when it is set), daily
   limit, text, problems and warnings.
5. With `run --yes` it uploads each video to Vercel Blob, schedules, and
   writes in the section `- Status: scheduled (YYYY-MM-DD HH:MM, <zone>).`
   and `- Buffer: <id>`. If a channel fails, it stops; the previous ones are
   already scheduled and recorded.
6. `sync --write` checks the records' scheduled posts: the sent ones move
   to `- Status: published (YYYY-MM-DD).` with their `- Link:`, it warns
   about those with an error and deletes the media of the ones already
   published.

## Flow with the user

1. Before proposing the schedule, tell the user that on
   every channel the cover is stuck on as the first 2 frames of the
   video (a barely noticeable flash at the start and on every loop, see
   "Cover and publishing on each channel"), because this skill sets the
   cover only as a frame of the video: a separate cover image is a
   paid-plan feature of Buffer that the CLI does not use (see "Media" in
   the `buffer-api` skill's `references/api.md`). If the workspace has a skill that publishes to
   Instagram directly with a real cover (publishing right away, without
   scheduling), mention it as the alternative. The user chooses the
   route.
2. Confirm that each channel has an approved caption, a time with a known
   time zone and, on YouTube, a title. If something is missing, ask for it
   with the agent's structured question tool (concrete times as options)
   and write it in `piece.md` before continuing.
3. `schedule plan <piece> --check` and present in the chat, per channel:
   time with its zone (and the secondary zone if configured), file and
   duration, full caption, YouTube title, category and privacy, queue and
   warnings.
   Open the control frame so they see the cover.
4. Ask for authorization with the structured question tool. Without an
   explicit yes, nothing is scheduled.
5. `schedule run <piece> --yes` and verify with `buffer queue`.
6. After the scheduled time, `schedule sync --write` and check the link.
   Check that `social/index.md` has the row with the channels the piece
   went to.

## Cover and publishing on each channel

With the cover stuck on as the first 2 frames (`COVER_FRAMES` in
`schedule.mjs`), the Instagram grid, the TikTok profile and YouTube's Shorts
tab show the cover, and the flash at the start and on every loop is
barely noticeable. TikTok may publish on its own or may send a notification
to finish the post in the app, depending on how the channel is connected:
check it on the first piece scheduled there. If a channel does not behave
as described, review it with the user
and adjust `COVER_FRAMES` or the channels that carry the
cover (`coverFrame`).

## Limits

- How many posts a channel can have scheduled, and how many channels the
  account can connect, depend on the Buffer plan (see "Plan limits" in the
  `buffer-api` skill's `references/api.md`). With `BUFFER_QUEUE_LIMIT` set
  to the plan's figure, the rehearsal warns when a queue is full; Buffer
  rejects the post if it really is.
- Buffer needs the video at a live URL until publication: do not delete the
  media of a pending post (`buffer media cleanup` already respects it).
- To change the time or cancel a scheduled post: `buffer post edit <id> --at
  "…" --tz <zone> --yes` or `buffer post delete <id> --yes`, and fix
  `piece.md` by hand.
- The script handles Instagram, TikTok and YouTube, in the Buffer
  organization `buffer-api` works on (the account's first, or the one
  `BUFFER_ORGANIZATION` names); other networks need another tool.
