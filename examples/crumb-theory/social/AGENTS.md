# Social pieces

How Crumb Theory keeps its short videos and other social pieces: one folder per piece, an index of all pieces and a record (`piece.md`) per piece. Read by `write-short-video-script`, `recommend-video-hook`, `edit-short-video`, `design-reel-cover`, `write-caption` and `schedule-social-piece`; the full workspace layout is in the repository's `CONVENTIONS.md`.

## Folder of a piece

```
social/
  index.md                      one row per piece, newest first
  YYYY-MM-DD-slug/
    piece.md                    the record (format below)
    script.md                   the script, beat map and verifications (write-short-video-script)
    hooks.md                    hook candidates and scores (recommend-video-hook)
    research.md                 claims ledger and kitchen test log (../operations/research-policy.md); broad dossiers go in reports/
    source/
      recording/                camera takes as they came off the camera, plus their transcripts
      broll/                    overhead shots, cross-section close-ups, photos of the samples
    edit/
      analysis/<video>/         transcripts, words.json and contact sheets (analyze-video)
      takes/                    sentences.json and choose-takes.html for sentence-by-sentence recording
      candidates/               sounds.json, choose-sounds.html, sfx/ and music/ to listen to (find-video-audio)
      proposal.md               the edit proposal the user approves (edit-short-video)
      space.json                the space map input
      project/                  the HyperFrames project and its assets/
      tests/                    test renders and frames checked at full size
    cover-src/                  cover sources: frames/, generated/, the cover HTML (design-reel-cover)
    cover-instagram.png         the approved cover
    export/<slug>-<channel>.mp4 the final video; a single <slug>.mp4 when all channels share it
```

- The folder's date marks when the piece was begun, not when it goes out; each channel's publication date is kept in `piece.md`.
- The slug says what the piece is about in two to four words (`soda-vs-powder`, `flat-cookies`), never the channel.
- Every file name is lowercase and hyphenated, with no spaces and no accented letters. A single camera take can be renamed `<slug>.<ext>` when it moves into `source/recording/`; clips from a sentence-by-sentence recording keep their camera names, lowercased, so their order survives.
- Create `source/recording/` and `source/broll/` as soon as the piece folder exists, so the creator can drop footage in right after filming. Other folders appear when a skill first needs them.
- Files in `source/` are never edited. Every render starts from them.

## When each file appears

- The folder and `script.md` appear with the first script draft. A script is always a file, never only a chat message.
- `piece.md` and the index row appear when the user approves the cover or the caption, whichever comes first.
- When a channel publishes, its section gets the date and the link. When metrics are shared, they go in that channel's section.
- Check `index.md` before suggesting a new piece, hook or cover concept, so ideas do not repeat and no pillar gets neglected. The index is usually enough; a record is opened only for a detail the index does not carry.

## Index

`index.md` is one table, newest first:

| Date | Piece | Type | Pillar | Hook | Channels | Cover concept |
|---|---|---|---|---|---|---|

- **Piece:** a short title linked to its record, `YYYY-MM-DD-slug/piece.md`; `schedule-social-piece` looks for that path to confirm the piece is indexed.
- **Type:** diagnosis, experiment, myth check, explainer or announcement.
- **Pillar:** the name from `../editorial/pillars.md`, or `none`.
- **Hook:** the template code from `recommend-video-hook` (for example `C4`), so the next pieces can rotate templates.
- **Channels:** `IG`, `TikTok`, `Shorts`, separated by ` · `.
- **Cover concept:** the image and the headline in quotes, in a few words.

When the table passes about 150 rows, move the previous years to `index-YYYY.md`.

## piece.md

The field names below are fixed: `schedule-social-piece` and the other skills read and write them.

````markdown
# <Working title>

- Status: draft | approved | published (YYYY-MM-DD)
- Time zone: America/Chicago
- Type:
- Pillar:
- Central idea: the takeaway, in a sentence.
- Hook: template code and name, then the first line in quotes.
- Source: `script.md` · camera take in `source/recording/` · support shots in `source/broll/`

## Edit

- Proposal: `edit/proposal.md` (approved YYYY-MM-DD)
- Export: `export/<slug>.mp4` or one file per channel, with its length
- Resources: the main devices used, in one line

## Audio

- Music and effects used, each with its source and license, and the credit text the caption must carry if the license asks for one. Detail in `../../media/audio/log.md`.

## Cover

- Concept: the image and why it opens the question without giving away the answer.
- Composition: what sits where.
- Headline:
- File: `cover-instagram.png` · source in `cover-src/`

## Instagram

- Status: approved
- Schedule: YYYY-MM-DD HH:MM
- Link:

Caption:

```
<approved caption>
```

## TikTok

(same fields as Instagram)

## YouTube

- Status: approved
- Schedule: YYYY-MM-DD HH:MM
- Title: <the Short's title>
- Privacy: public
- Category: <YouTube category id, for example 26 for Howto & Style>
- Link:

Caption:

```
<approved description>
```
````

Field rules:

- **Channel headings** are exactly `## Instagram`, `## TikTok` and `## YouTube` (or `## YouTube Shorts`). Other sections (`## Edit`, `## Audio`, `## Cover`) can sit before them in any order.
- **Time zone** goes in the header, before the first `##` section, as an IANA name. A single channel can override it inside its own field: `- Schedule: 2026-11-24 18:30 (America/New_York)`.
- **Status** in a channel section moves through `draft`, `approved`, `scheduled (YYYY-MM-DD HH:MM, <zone>).` and `published (YYYY-MM-DD).`. Only `approved` sections are scheduled; `schedule-social-piece` writes the last two.
- **Schedule** is `YYYY-MM-DD HH:MM`, 24-hour clock.
- **Caption:** the word on its own line, a blank line, then the text inside a code block. On YouTube this is the description.
- **Title** (YouTube only) is required to schedule: up to 100 characters, without `<` or `>`. **Privacy** is `public`, `unlisted` or `private`, public when absent.
- **Buffer:** the post id, written by `schedule-social-piece`; a section with an id is not scheduled twice.
- **Link:** the post URL, written when it is published.
- **AI: yes** goes in the header only when the piece contains generated images or voice that the platforms ask to disclose; it flags the piece as AI-generated on every channel. Leave the line out otherwise.
- After publishing, each channel's section gets its 7-day metrics: views, reach, saves, shares and profile visits on Instagram; the equivalents the other platforms report.
- A record shows where the piece stands now. Drafts, rejected hooks and the story of how the design evolved belong elsewhere or nowhere.

## Cleanup after publishing

Once every channel is live, and only if the user asks to free disk space:

- Can go to the system trash: `source/`, `edit/candidates/`, `edit/tests/`, the video proxies in `edit/takes/` (keep `sentences.json`), heavy media inside `edit/project/` (b-roll copies, renders, caches) and the `export/*-buffer.mp4` files `schedule-social-piece` generated.
- Keep: `piece.md`, `script.md`, `hooks.md`, `research.md`, `edit/proposal.md`, the text and JSON files of `edit/analysis/` (with the transcript of the final video), the project's `index.html` and scripts, and `cover-src/`.
- Before removing the upload export, make an archive copy `export/<slug>-archive.mp4` at a smaller size (for example `ffmpeg -i export/<slug>.mp4 -c:v libx265 -crf 26 -preset slow -tag:v hvc1 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart export/<slug>-archive.mp4`) and compare a frame with subtitles at full size against the original before trashing it.
- Before removing `source/`, make sure `edit/analysis/` has the transcript of the final video; if not, run `analyze-video` on the export first.
- Always move to the trash, never delete permanently, so the user can recover anything removed by mistake.
