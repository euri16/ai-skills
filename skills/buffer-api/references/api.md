# Buffer API: contracts and limits

Single endpoint `POST https://api.buffer.com` (GraphQL), header
`Authorization: Bearer <key>`. Full reference:
[developers.buffer.com/reference](https://developers.buffer.com/reference.html).
Figures and behaviors quoted from Buffer's public pages were read on
2026-11-20; Buffer changes them, so read the linked page before relying on
one.

## Key

- Treat the personal key as access to the whole account. How many keys
  an account can have depends on its plan ("Plan limits"). How to create and
  store it: Prerequisites in `SKILL.md`.
- If the CLI exits with code 3, the variable is missing or the key was
  revoked or deleted: the user generates another and sets
  it; the agent never sees it.

## Account and channels

The CLI reads the account (`account{organizations}`) and works on one
organization: the one `BUFFER_ORGANIZATION` names by id or name, or the
account's first. It lists that organization's channels (`channels`) and
resolves `--channel` by id, service (`instagram`, `tiktok`, `youtube`) or
channel name, so reconnecting a channel (new id) breaks nothing. Run
`buffer channels` or `buffer doctor` to see what the account has. The CLI
never requests or prints the account's email.

## Operations

| Operation | Use in the CLI |
|---|---|
| `account`, `channels` | `whoami`, `doctor`, `channels` |
| `posts` (filter `status`, `channelIds`, `dueAt`; cursor pagination) | `queue`, `posts list` |
| `post` | `post get`, `metrics post` |
| `dailyPostingLimits` | `post create` plan |
| `createPost` with `saveToDraft` | `post create --check`, `--draft` |
| Scheduled `createPost` (`customScheduled`) | `post create --yes` |
| `editPost` (full post: text, assets, metadata) | `post edit` |
| `deletePost` | `--check`, `post delete` |
| `aggregatedPostMetrics` | `metrics aggregate` |
| `Post.metrics` | `metrics post` |
| `ideas`, `createIdea` | `ideas list`, `ideas create` |

`CreatePostInput` used: `channelId`, `mode` (`addToQueue`, `shareNext`,
`shareNow`, `customScheduled` with `dueAt` ISO UTC), `schedulingType`
(`automatic` or `notification`), `text`, `assets` (`video{url,
metadata{thumbnailOffset}}` or `image{url, metadata{altText}}`), `metadata`
(`instagram{type, shouldShareToFeed, isAiGenerated, firstComment}`,
`youtube{title, categoryId, privacy, isAiGenerated, madeForKids}`,
`tiktok{isAiGenerated, title}`), `saveToDraft`, `aiAssisted`. Buffer's
reference marks `youtube.title` and `youtube.categoryId` as required on
create and optional on edit, where an omitted value keeps the existing one
(read 2026-11-20); the CLI sends the category from `--category` or
`BUFFER_YOUTUBE_CATEGORY` and blocks a YouTube post that has neither. Mutations return a union: success (`PostActionSuccess`,
`DeletePostSuccess`, `Idea`) or an error with `message`.

## Plan limits

Every limit below depends on the account's Buffer plan and Buffer changes
them: read the linked page, or the account's settings, before relying on a
figure. The CLI assumes none of them. It reads the request quota from the
`RateLimit` header of every response and warns with fewer than 15 requests
remaining in any window, and it warns about a full queue only against the
figure the user declares in `BUFFER_QUEUE_LIMIT`.

- **API requests** ([API limits guide](https://developers.buffer.com/guides/api-limits.html)):
  three windows, 15 minutes, 24 hours and 30 days. For the Free,
  Essentials and Team plans the guide gives 150, 450 and 1,500 requests
  per 15 minutes; 600, 1,800 and 6,000 per 24 hours; and 1,000, 3,000 and
  10,000 per channel every 30 days, with a cap per plan. All the API keys
  and MCP connections of an account share one set of limits. Each response
  carries one `RateLimit` policy per window, with `r` (requests remaining)
  and `t` (seconds until the window resets). Over a limit the API answers
  429 with `Retry-After`, and a 429 does not consume quota.
- **API keys:** the API limits guide gives 1, 3 and 5 keys for those plans
  and the [pricing page](https://buffer.com/pricing) gives 5 on every
  plan; the account's settings show the real figure.
- **Channels, queue, ideas and paid features** (pricing page): the Free
  plan allows up to 3 channels, 10 scheduled posts per channel (freed when
  they publish) and 100 ideas, and it has neither first comment scheduling
  nor custom video covers. A channel over the plan's limit shows as locked.
- **Posts per day** ([daily posting limits](https://support.buffer.com/articles/daily-posting-limits-kJ0JtpsdvD)):
  per channel and per 24 hours, 50 on Instagram (posts, Reels and Stories
  together) and 25 on TikTok; on YouTube Shorts it depends on the plan and
  on whether the Buffer email is verified. The CLI reads the real figure
  of each channel with `dailyPostingLimits`.
- **Aggregated metrics:** how far back they reach depends on the plan; the
  CLI warns when a range starts more than 31 days ago.

## Media

- No upload endpoint: Buffer receives a public URL and downloads it when the
  post is created (reads duration and size) and again when publishing. A URL
  that expires or is deleted before then makes the publication fail. The CLI
  uploads local files to Vercel Blob (`vercel blob put --access public`)
  with `BLOB_READ_WRITE_TOKEN`; the file is public at that URL until it is
  deleted.
- Instagram ([Buffer's Instagram guide](https://support.buffer.com/articles/using-instagram-with-buffer-YSjg2dXFV8)):
  a Reel of 5 seconds to 15 minutes and up to 300 MB; a Story video of 3 to
  60 seconds. The CLI checks the Reel figures and accepts up to 20 items in
  a carousel, Instagram's own limit. Text, a link, stickers or music turn a
  Story into a notification.
- TikTok ([Buffer's TikTok guide](https://support.buffer.com/articles/using-tiktok-with-buffer-oGEroY9Of2)):
  a video of 3 seconds to 10 minutes and up to 1 GB, 5 hashtags per post.
  The CLI checks the duration and warns about the hashtags.
- YouTube ([Buffer's YouTube Shorts guide](https://support.buffer.com/articles/using-youtube-shorts-with-buffer-Jl8iR6jIck)):
  Shorts only, up to 3 minutes, title required; Buffer does not support a
  custom thumbnail for Shorts.
- Video cover: the CLI sets it only as a frame of the video
  (`thumbnailOffset`, in ms). Custom video covers are a paid-plan feature
  on Buffer's pricing page, and the CLI does not use them.

## Text (UTF-16 units)

From Buffer's [character limits guide](https://developers.buffer.com/guides/character-limits.html):
Instagram 2,196, where each line break counts 2 (Buffer's Instagram guide
says 2,200; the CLI applies the lower figure) · TikTok 2,200 with a video ·
YouTube 5,000 for the description and 100 for the title, no `<` or `>`.
In UTF-16 units most emoji and the Unicode "bold" letters count double.

## Dated deprecations

From Buffer's [reference](https://developers.buffer.com/reference.html):

- 2026-12-01: several `PostMetricType` values are removed (`favorites`,
  `replies`, `retweets`, `reblogs`, `repins`, `other`, `link_clicks`). The
  CLI uses the normalized ones.
- 2026-12-15: `AssetInput.link` is removed (use
  `metadata.<network>.linkAttachment`). The CLI does not use it.
