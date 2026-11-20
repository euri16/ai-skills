# Safe operations with Buffer

## Write protocol

1. Rehearsal without `--yes`: the CLI shows the plan and validates locally
   (text, media, time, queue, daily limit, channel).
2. If server certainty is needed, `--check`: a temporary draft that is
   deleted on the spot along with its media.
3. Present the full plan to the user: channel, time with
   its zone (and the secondary zone if configured), file, cover, full text
   and title.
4. Authorization with the agent's structured question tool (for example
   `AskUserQuestion`).
5. One run with `--yes`. Do not retry in a loop: if it fails, read the state
   (`queue`, `posts list --status draft,error`) before repeating, so as not
   to duplicate posts.
6. Verify with `post get <id>` or `queue`.

## What is irreversible

- A scheduled post goes out on its own at its time even if the computer is
  off. To cancel it, `post delete <id> --yes` before that time.
- `--mode now` publishes instantly.
- Deleting in Buffer a post already sent does not remove it from Instagram,
  TikTok or YouTube: that is done in each network's app.
- Ideas cannot be deleted through the API.

## Pitfalls

- The `--dry-run` of Buffer's official CLI (`@bufferapp/cli`) only builds
  the request locally. To validate against the server, `--check`.
- Buffer silently switches to notification publishing when the post carries
  something the network does not let third parties publish (Stories with
  text or a link, music on photo posts, aspect ratio out of range). The CLI
  warns if the response carries another `schedulingType`. In notification
  mode, `sent` only means the notification was sent, and without a phone
  with the Buffer app nothing arrives.
- The media must stay alive until publication. Never delete by hand a blob
  listed in the media registry (`BUFFER_STATE_DIR/media.json`) with a
  pending post; `media cleanup` already respects them. Losing the registry
  means `media cleanup` can no longer find those blobs, so keep it in a
  stable, git-ignored folder of the workspace.
- The URL of a deleted blob may keep responding 200 for a few seconds
  because of the cache; without cache it gives 404.
- `posts list` also includes posts already published on the networks,
  imported by Buffer, with status `sent`. For what is scheduled, filter
  `--status scheduled`.
- In `posts`, the `startDate` filter returns an empty list even when there
  are posts in the range; filter by date with `dueAt: {start, end}`, which
  on sent posts matches `sentAt`.
- The channels' time zone in Buffer only affects `--mode queue` and the day
  that counts toward the daily limit; `--at` always sends the exact time in
  UTC.
- `editPost` replaces the whole post: with only `id` and `dueAt` it fails
  with "Post must have either text or media" and the channel's required
  fields. `post edit` reads the post and sends again its text, media (same
  URL and `thumbnailOffset`), publishing type and channel metadata
  (Instagram type and feed, YouTube title, category and privacy, AI flags),
  changing only what was asked; the rehearsal lists what it keeps.
- On a plan that caps scheduled posts per channel, that cap runs out long
  before the request quota. Declare it in `BUFFER_QUEUE_LIMIT` so the plan
  and `doctor` warn about it.
