# Sources and licenses

Sources reviewed on 2026-10-27; the terms of Freesound, myinstants, Pixabay and Mixkit and the pages of Incompetech were read again on 2026-11-20. Licenses and terms change, so check them again before relying on a source for something important. Default: free sources with a known license. Record the license and origin of every file.

## With API (the agent can search and download)

| Source | What it has | Access | Licenses | Platforms | Attribution | Risk |
|---|---|---|---|---|---|---|
| Freesound | SFX, loops, some music | API v2 with token (`FREESOUND_API_KEY`); text search with license, duration and tag filters; the search returns the URL of each high-quality MP3 preview; the original file requires OAuth2. Standard rate: 60 requests per minute and 2,000 per day ([API overview](https://freesound.org/docs/api/overview.html)) | "Creative Commons 0", "Attribution" and "Attribution NonCommercial". `freesound-search.sh` searches CC0 by default, CC BY on request, and never lists or downloads anything else | Any | CC BY: "Sound: <name> by <author> (CC BY 4.0)" in the caption; CC0 none | "You can use the Freesound API for free only for non-commercial purposes. To use the Freesound API for commercial purposes, please contact us" ([API terms](https://freesound.org/docs/api/terms_of_use.html)). Whether the user's use is commercial is theirs to judge, and arranging it with Freesound is their responsibility: tell them so the first time the key is used |
| Jamendo | Music | API | Almost all CC BY-NC or ND | Not usable for sync in brand video | | Discard unless a specific CC BY track |
| ccMixter | Remix music | Old query API (`lic=by`) | CC BY and CC BY-NC | CC BY only | Credit | Uneven catalog |

## Without API (manual download with receipt, except Incompetech)

| Source | License | Platforms | Attribution | Note |
|---|---|---|---|---|
| Pixabay (music and SFX) | Pixabay Content License: commercial use, no credit | Any | No | Its API covers only images and video, and its [terms](https://pixabay.com/service/terms/) forbid automated collection and bulk copying: the user downloads by hand. It forbids redistributing the audio on its own (as a pack or library) and using recognizable brands in commercial use. Some authors register their music in Content ID: the claim is withdrawn with the license, but not avoided. Save the page link and, for music, the download's license certificate; prefer its SFX to its music. License reviewed on 2026-10-27 (version of October 20, 2026) |
| Mixkit | Mixkit License: social media, YouTube and online ads yes; TV, radio, games and records no | Social media and YouTube | No | Good catalog of interface SFX and whooshes. Its [terms](https://mixkit.co/terms/) forbid using "scripts or bots to mass download Items": the user downloads by hand |
| Bensound | Free with credit | Any | Yes: "Music: Bensound.com" with the title | Small but clean catalog. Its terms on automated downloading are not verified: the user downloads by hand |
| Incompetech (Kevin MacLeod) | CC BY 4.0 | Any | Yes, at the end of the caption, with the text its [FAQ](https://incompetech.com/music/royalty-free/faq.html) asks for: "<title> Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0. https://creativecommons.org/licenses/by/4.0/" | Classic stock music, and the one source of this table the agent downloads from: its [page for automated agents](https://incompetech.com/agent-section/) publishes the catalog (`https://incompetech.com/music/royalty-free/pieces.json`, with a `filename` per track) and the folder of the MP3 files, and neither that page nor the FAQ sets a limit on automated downloads. Download one chosen track at a time with `curl -fL "https://incompetech.com/music/royalty-free/mp3-royaltyfree/<filename with spaces as %20>"`, never the catalog in bulk. Useful for energetic beds when there is no Freesound key |
| Uppbeat (free plan) | Free with credit, individuals only, monthly download limit | Social media and YouTube | Yes, text provided by the platform | Manual download by the user |
| YouTube Audio Library | Free for YouTube; outside YouTube it does not say | Shorts safe; the rest, gray area | Per track | Only if the piece is mainly for YouTube |

Attribution texts go in the caption's language; the formats above show the structure.

## Sources outside the default

**myinstants** (user-uploaded sounds: effects, phrases, clips). Off by default, because this skill promises sounds with a known license and this source has none. Read on 2026-11-20 in its [terms of use](https://www.myinstants.com/en/terms_of_use.html):

- No license is declared for the sounds. The uploader licenses them to the site only, and the site says it is "not responsible for any User Content".
- The site grants "a non-transferable, non-exclusive, revocable, limited license to access the Site solely for your own personal, noncommercial use".
- Users agree not to "generate automated searches, requests, or queries to the Site", so the agent does not query it.
- Much of the catalog is material from films, songs and broadcasts, which can be claimed or muted on the platforms.

Use it only when the user asks for it after being told those four points; the decision and its consequences are theirs, and the user downloads the file by hand. Even then, discard anything that is a fragment of a film, a series, a game or a song, record each file as "origin without declared license" with its link and the author as "unknown (myinstants user)", and prefer an equivalent with a known license when one exists.

**Paid libraries** (Epidemic Sound, Artlist, Soundstripe and similar, and paid generators such as Mubert, Soundraw or ElevenLabs). Outside the default of free sources. Use one only when the user has a license for it and says so; they download the files, and each one is registered with that license.

## What does not work

- In-app libraries (Meta Sound Collection, TikTok Commercial Music Library): they only work with audio added in the app, not with audio burned into the MP4 that is uploaded to every platform the user publishes on. A professional Instagram account also loses commercial music.
- Suno and Udio: no public API, ongoing litigation with record labels and changing terms; do not use in production.
- Meta's MusicGen: weights under a non-commercial license.
- BBC Sound Effects: RemArc license, non-commercial and educational use only.

## Local generation models (not operated by this skill)

This skill ships no command for these models and has not verified them. They are listed so the user knows what exists and what each license allows, if they decide to install one on their own.

- **ACE-Step 1.5** (MIT license; repository `ace-step/ACE-Step-1.5` on GitHub, weights on Hugging Face): music generation with control of duration, BPM and key. Training data provenance not declared: that is the risk to accept if it is used.
- **Stable Audio Open Small** (Stability Community License, free below 1 M USD in revenue): SFX and loops of up to 11 s from text.

A generated file enters the library like any other: verified, approved by ear and registered with origin "generated locally (<model>)", the prompt and the seed in its inventory row.

## Labeling generated audio

YouTube asks to disclose synthetic content only when it is realistic and prominent; generated background music does not qualify. TikTok and Meta do not require a label for background audio. Recommendation: an optional line in the caption when the music is generated ("Music generated locally with AI").

## Register

Two files in `media/audio/`, as `CONVENTIONS.md` of the ai-skills repo defines them, plus the piece record. Column names are written in the user's language.

`inventory.md` describes the library: one row per file, grouped under a heading per folder. A file enters with its row and leaves with it.

```markdown
## sfx/hits-and-impacts

| File | Duration s | Origin (source, URL, author) | License | Required attribution | Notes |
|---|---|---|---|---|---|
| <file> | 0.24 | Freesound, https://freesound.org/s/<id>/, <author> | CC0 | None | System sound: cut hit A |
```

- Origin: the source, the page link and the author; "unknown (myinstants user)" when the source does not give one; "generated with `scripts/<generator>`" with its arguments for the brand motif sounds.
- Notes: what the next piece needs to know about the file: the system role it holds, where the hit or the landing falls inside the file, limits such as "sketch only".

`log.md` records use: one row each time a piece prepares or uses a file, newest first.

```markdown
| Date | Piece | File | Prepared | Used for | License and credit |
|---|---|---|---|---|---|
| 2026-11-19 | 2026-11-16-<slug> | sfx/hits-and-impacts/<file> | Trimmed, sample peak -3 dBFS | Cut hit at 0.9 s and 12.4 s | CC0, no credit |
```

Each piece's `piece.md` has an Audio section with the files used and the attribution text that must go in the caption.
