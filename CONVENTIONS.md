# Workspace conventions

The video editing skills in this repo assume the agent runs inside a **workspace**: a folder (usually a git repo) that holds the creator's brand, their pieces and their media library. This file describes that layout. Every skill refers here instead of explaining it again.

None of these files is mandatory. A skill reads what exists, skips what does not and says so. The more of the brand you write down, the less you have to repeat in every conversation.

## Layout

```
brand-guide/
  positioning.md          who the creator is, what they promise, what they are not
  audiences.md            who the content is for
  voice-and-humor.md      how the creator sounds, humor rules, forbidden patterns
  writing-style-playbook.md   detailed writing rules (optional)
  visual-identity.md      palette, typography, logo, graphic line, visual checklist
  motion.md               how things move and sound: easing, durations, physical effects, sound identity, closing gesture if the brand has one
  visual-ideation.md      how to brainstorm visual directions for a piece (optional)
  assets/
    fonts/fonts.css       stylesheet that loads the brand fonts: @font-face rules for local files or an @import of a web font service
    icons/  logo/  textures/
editorial/
  pillars.md              content pillars
  <channel>.md            one guide per channel (instagram.md, linkedin.md, ...)
  hook-references.md      hooks from creators the user likes, analyzed (recommend-video-hook)
  series/<series>/series.md   plan of a recurring series (intro, visual kit)
operations/
  research-policy.md      what must be verified and how
  review-and-approval.md  what needs the user's approval before going out
reports/                  research dossiers and decision reports, as YYYY-MM-DD-<slug>.md
social/
  AGENTS.md               piece conventions for this workspace
  index.md                one row per piece: date, piece (link `YYYY-MM-DD-slug/piece.md`), type, pillar, hook (template code), channels, cover concept
  YYYY-MM-DD-slug/        one folder per piece (see below)
media/
  AGENTS.md               how incoming material is handled
  inbox/                  material that has not been sorted yet
  broll/<topic>/          reusable b-roll
  references/             visual references
  audio/
    sfx/<type>/           sound effects by type (see find-video-audio)
    music/<mood>/         music by mood
    inventory.md          every library file with duration, origin, license and notes
    log.md                what was prepared and used, piece by piece
```

`examples/crumb-theory/` contains a complete profile of a fictional brand you can copy and rewrite.

## A piece folder

```
social/YYYY-MM-DD-slug/
  piece.md                the record: status, hook, caption per channel, schedule, edit, audio, metrics
  script.md               the script (write-short-video-script)
  hooks.md                hook candidates (recommend-video-hook)
  research.md             thesis, angle and verified claims (research-content-topic)
  cover-<channel>.png     the approved cover of each channel (design-reel-cover)
  source/
    recording/            the creator's camera takes or voice-over recording, never modified
    broll/                support clips, screenshots and photos
  edit/
    analysis/<video>/     transcripts, words.json, contact sheets (analyze-video)
    analysis/takes.json   every take of a sentence-by-sentence recording, transcribed (analyze-video)
    takes/                sentence-by-sentence takes: sentences.json, choose-takes.html
    candidates/           sounds.json, choose-sounds.html, labels.json, sfx/, music/ (find-video-audio)
    cuts.json             the cut list of a single-take recording (edit-short-video)
    proposal.md           the edit proposal the user approves (edit-short-video)
    space.json            the space map input
    project/              the HyperFrames project: clip.mp4 or voice.wav, cut.json and assets/ (sfx/, music/)
    tests/                test renders and frame reviews
  cover-src/              cover sources: frames/, generated/ (design-reel-cover)
  export/<slug>-<channel>.mp4
```

`piece.md` has a header (`- Status:`, `- Time zone: <IANA zone>`, `- Source:` linking `script.md`, `- Hook: <code> <template name>: "<line>"`) and one section per channel, plus `## Edit`, `## Audio` and `## Cover` sections that the edit, sound and cover skills fill. Scripts read and write these fields, so their names are fixed: `- Status:` (`draft`, `approved`, `scheduled (YYYY-MM-DD HH:MM, <zone>).`, `published (YYYY-MM-DD).`), `- Schedule: YYYY-MM-DD HH:MM`, `Caption:` followed by the text in a code block, `- Title:`, `- Privacy:` and `- Category: <id>` (YouTube), `- AI: yes` when the content is AI-generated (in the header for every channel, or in one channel's section), `- Link:` and `- Buffer:`. `schedule-social-piece` documents each one.

The date is the day the piece starts. The slug describes the piece, not the channel. Camera originals in `source/` are never modified: every render starts from them.

## Language

Skills, scripts and file names are in English. What the user reads (chat, questions, proposals, pages) is written in the user's language, or in the one the workspace instructions (`AGENTS.md`, `CLAUDE.md`) set. Content (scripts, captions, on-screen text) is written in the language of the piece.

## Approvals

Nothing is published, scheduled, sent or deleted without the user's explicit approval. Skills that ask questions use the agent's structured question tool when it has one and always show the full text being approved.

## Secrets

Credentials come from environment variables, listed in each skill's `SKILL.md`. Never commit them to the workspace. Local state files that skills write (for example Buffer's media cache) go in a git-ignored folder of the workspace.
