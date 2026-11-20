---
name: buffer-api
description: Operates the user's Buffer account through the `buffer` CLI over Buffer's official GraphQL API. Use it ALWAYS when the task touches Buffer programmatically, such as scheduling a post, checking the queue, changing a post's time, deleting a scheduled post, checking how much queue space is left, reading Buffer metrics or ideas, or checking the Buffer connection. Covers channel status, queue and limits, creating, editing and deleting posts (Instagram Reel, post and Story, TikTok video and photos, YouTube Shorts), real validation with a temporary draft, media upload to Vercel Blob and its cleanup, per-post and aggregated metrics, ideas and any query via `raw`. To schedule a piece from `social/` use `schedule-social-piece`, which depends on this one.
---

# Buffer API

Official connection to Buffer with a personal API key (Settings › API), no
MCP. Everything goes through the `buffer` CLI (`scripts/buffer.mjs`, no
dependencies). The CLI discovers the account's organization and channels at
runtime, so nothing about the account is configured in the skill. It works
on one organization (the account's first, or the one `BUFFER_ORGANIZATION`
names) and validates posts for Instagram, TikTok and YouTube; a post for
another service gets only the text-length check.

## Prerequisites

Check these when the skill is invoked, before doing anything else. Check that environment variables are set without printing their values. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| Node.js 18 or later | Yes | Running the CLI | `brew install node` or the installer at https://nodejs.org |
| A Buffer account with its channels connected | Yes | Every operation | Sign up at https://buffer.com and connect the channels (for example Instagram, TikTok and YouTube) in Buffer |
| `BUFFER_API_KEY` | Yes | Every API call. Never printed | Create a personal key at https://publish.buffer.com/settings/api and export it as `BUFFER_API_KEY` from the shell profile or a secret manager, never from a file in the workspace or a repository |
| `BUFFER_TIMEZONE` | No | The IANA zone of `--at "YYYY-MM-DD HH:MM"` when `--tz` is not passed. There is no default: without it or `--tz`, `--at` fails. Reads fall back to the machine's zone for display | `export BUFFER_TIMEZONE=<IANA zone>`, for example `America/New_York` |
| `BLOB_READ_WRITE_TOKEN` | No | Uploading or deleting local media (`--file` and `--files` with `--check` or `--yes`, `media put`, `media cleanup`, `post delete` of a post with uploaded media). Not needed with `--url`, also under `--check`. An uploaded file gets a public URL: anyone with the link can open it until it is deleted, so upload only what is going to be published | Create a Blob store in a Vercel project (Storage › Blob), copy its read/write token and export it as `BLOB_READ_WRITE_TOKEN` |
| `vercel` CLI | No | The Blob uploads and deletions above | `npm install -g vercel` |
| `ffprobe` | No | Duration, size and codec checks of local videos in the plan | `brew install ffmpeg` (it includes `ffprobe`); on Linux, `sudo apt install ffmpeg` |
| `BUFFER_YOUTUBE_CATEGORY` | No | The YouTube category id of a Short when `--category` is not passed. There is no built-in default: without either, a YouTube post is blocked, because Buffer requires a category to create it | `export BUFFER_YOUTUBE_CATEGORY=<id>`, with the id of the category the channel publishes in (for example 22 People & Blogs, 26 Howto & Style, 28 Science & Technology) |
| `BUFFER_QUEUE_LIMIT` | No | How many scheduled posts per channel the account's Buffer plan allows. With it, the plan and `doctor` warn when a queue reaches it; without it, no limit is assumed and Buffer itself rejects a post over the plan's limit | `export BUFFER_QUEUE_LIMIT=<number>`, with the figure of the account's plan (see "Plan limits" in [api.md](references/api.md)) |
| `BUFFER_SECONDARY_TIMEZONE` | No | A second IANA zone shown next to the local time in plans | `export BUFFER_SECONDARY_TIMEZONE=<IANA zone>` |
| `BUFFER_STATE_DIR` | No | Folder of the uploaded-media registry (`media.json`). Default `<workspace>/.buffer-state` | Export it to use another folder; either way, add the folder to the workspace's `.gitignore` |
| `WORKSPACE_ROOT` | No | The user's workspace. Default: the current directory | `export WORKSPACE_ROOT=<path to the workspace>` |
| `BUFFER_API_URL` | No | API endpoint override. Default `https://api.buffer.com` | Leave it unset except to test against another endpoint |
| `BUFFER_ORGANIZATION` | No | The Buffer organization the CLI works on, by id or name, when the account has several. Default: the account's first | `export BUFFER_ORGANIZATION=<id or name>`; `buffer whoami` lists them |

A missing variable stops the CLI with a message that names it.

## The CLI

```bash
buffer() { node <skill-dir>/scripts/buffer.mjs "$@"; }
buffer whoami          # account id, time zone and organizations (it never prints the account's email)
buffer doctor          # account, channels (connection, lock, pause, zone, scheduled posts, phone), quota and warnings
buffer queue           # scheduled posts per channel, in the configured zone
buffer posts list --status sent --channel tiktok --limit 5
buffer metrics post <id>
buffer help
```

Exit codes: 0 ok · 1 API error · 2 local validation · 3 missing or invalid
key · 4 rate limit.

## Rules

- Reads need no confirmation. Every write (creating, editing or deleting
  posts, creating ideas, `media cleanup`, `raw mutation`) is first rehearsed
  without `--yes`, the full plan is presented to the user,
  authorized with the agent's structured question tool (for example
  `AskUserQuestion`), run once with `--yes` and verified with a read
  (`post get`, `queue`).
- Write everything the user reads (chat, questions,
  plans) in the user's language, or the one the workspace instructions set.
- `--check` does not publish: it uploads the media, creates a draft, reads
  it and deletes the draft and the media on the spot. It can be used without
  approval to validate on the server, reporting that it was done.
- Scheduling is a deferred public action: whatever enters the queue goes out
  on its own at its time. Never schedule without an approved piece record
  (`social/<YYYY-MM-DD-slug>/piece.md`) or without the user
  having seen the exact text, the file and the time.
- The time is always written as `YYYY-MM-DD HH:MM` in the zone given by
  `--tz` or `BUFFER_TIMEZONE`, and the CLI converts it to UTC. When
  presenting the plan, show the local time with its zone, and the secondary
  zone if `BUFFER_SECONDARY_TIMEZONE` is set.
- Never print or log the key or the Blob token. If one appears in an
  output, it is a bug: fix it in `buffer.mjs` before continuing.
- Keep a single API key and no MCP: every key and MCP connection of an
  account shares one set of rate limits (see "Plan limits" in
  [api.md](references/api.md)), so a second client only spends the same
  quota.

## Create a post

```bash
buffer post create --channel instagram --file social/<piece>/export/<slug>-instagram-buffer.mp4 \
  --text-file /path/caption.txt --at "2026-11-10 19:00" --tz America/New_York   # plan
buffer post create … --check                                                    # real validation, no trace
buffer post create … --yes                                                      # schedules
```

- `--channel`: `instagram`, `tiktok`, `youtube` (resolved by service among
  the account's channels), the channel name or the channel id.
- Media: `--file` (uploaded to Vercel Blob), `--files a,b` (carousel) or
  `--url` if it is already public. The uploaded file is recorded with its
  post in the media registry (`BUFFER_STATE_DIR/media.json`) and must stay
  alive until Buffer publishes.
- Instagram: `--type reel|post|story`. Without it, one video is a Reel
  and anything else a post. The CLI does not restrict which type a video
  takes: Buffer decides, so validate another combination with `--check`.
  `--no-feed` to not share the Reel to the grid, `--ai` to flag
  AI-generated content, `--first-comment "…"` to add a first comment (it
  depends on the plan; the CLI warns that Buffer may reject it). Cover: `--thumb-offset` in ms,
  the frame of the video used as its cover (0 by default; see "Media" in
  [api.md](references/api.md) and, for a designed cover,
  `schedule-social-piece`).
- YouTube: `--title` required (100 characters, no `<` or `>`),
  `--privacy public|unlisted|private` (public by default), `--category
  <id>` or `BUFFER_YOUTUBE_CATEGORY` (required: one of the two, the CLI
  imposes no category), `--made-for-kids` to flag the video as made for
  kids. Only Shorts of up to 3 minutes.
- TikTok: the text is the caption (2,200 characters with video, 5 hashtags).
- `--mode queue|next|now` instead of `--at`: next slot in the schedule,
  first in the queue or publish now (`now` is immediate with `--yes`).
- `--notify` schedules as a mobile notification; the CLI rejects it if there
  is no phone with the Buffer app and notifications.
- `--draft` creates a draft in Buffer without scheduling it.

The plan shows channel, mode, time (local with its zone, UTC and the
optional secondary zone), media with duration and codec, cover, YouTube
category and privacy, text and its length, the channel's scheduled posts
(with the limit when `BUFFER_QUEUE_LIMIT` is set) and daily limit, and lists
problems (blocking) and warnings. A queue at the declared limit is a
warning, not a problem: the limit is the user's figure, and Buffer has the
last word.

## Edit, delete and clean up

- `buffer post edit <id> --at "…" --tz <zone>` or `--text-file f`, with
  `--yes`. Only scheduled posts, drafts or posts with an error.
- `buffer post delete <id> --yes` deletes the post and its uploaded media. A
  post already sent does not disappear from the social network when deleted
  in Buffer.
- `buffer media cleanup` shows which uploaded files can be deleted: those of
  sent or deleted posts, and those that have gone more than 24 h without a
  post. It keeps those of pending posts or posts with an error. Deletes with
  `--yes`.

## Metrics and ideas

- `buffer metrics post <id>`: normalized post metrics (views, reach,
  reactions, comments, shares, saves, averageTimeWatched…), updated once a
  day. Also works with posts that did not go out through Buffer.
- `buffer metrics aggregate --channel tiktok --since YYYY-MM-DD`: aggregate
  for the range; some plans only return the last 31 days, and the CLI
  warns when the range starts earlier.
- `buffer ideas list` and `buffer ideas create --title … --yes`. The API
  does not edit or delete ideas, and the plan caps how many there can be.
- If the workspace has a metrics-sync skill, it keeps the weekly history;
  otherwise read metrics on demand with these commands.

## Self-healing: close every process by updating the skill

The API changes often ([changelog](https://developers.buffer.com/changelog.html)).
When finishing any operation:

1. If a mutation or field responded differently from what is documented, fix
   `buffer.mjs` and [api.md](references/api.md) in the same turn.
2. Unexpected behaviors (switch to notification, media rejection, limits)
   go to [safe-operations.md](references/safe-operations.md) as a
   current pitfall in the present tense.
3. Before the deprecation dates in `api.md`, check that the CLI does not use
   what is being removed.

Changes are integrated into their section as a current instruction, without
history.

## References

- [api.md](references/api.md): key, account and channel discovery,
  operations used, plan limits and deprecations.
- [safe-operations.md](references/safe-operations.md): write protocol,
  what is irreversible and pitfalls.
