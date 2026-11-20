# Media library

The shared library: footage, photos and sound that several pieces can draw on. Read by `edit-short-video` when material arrives through the inbox, and maintained by `find-video-audio` for everything under `audio/`. Material of one piece lives in that piece's folder in `../social/`.

## Structure

```
media/
  inbox/                  drop zone: the creator leaves new footage, photos or audio here
  broll/<topic>/          shots reused across pieces: broll/oven/, broll/flour-dust/, broll/mixing/
  references/<topic>/     other creators' work kept only for study: references/covers/, references/edits/
  audio/
    sfx/<type>/           sound effects by type, as listed in find-video-audio
    music/<mood>/         music beds by mood
    inventory.md          every library file: duration, origin, license, notes
    log.md                which file was prepared and used in which piece, with its license and credit
```

## Inbox

- The inbox is a tray, not storage. Anything that lands there is sent on to its piece: the camera take to `../social/<piece>/source/recording/`, overhead shots, cross-sections and photos to `../social/<piece>/source/broll/`, or to `broll/<topic>/` if several pieces will use it.
- Rename on the way out: lowercase, hyphens, no spaces or accents.
- A file with no obvious home stays put until the user says where it goes.
- Throwaway inputs (a screenshot shared for context, a sound check) are trashed after the task, once the user agrees.

## B-roll

- Organized by subject, not by date: `broll/oven/`, `broll/proofing/`, `broll/cutting/`.
- Only footage the creator shot or footage with a license that allows reuse; the license goes in a `README.md` inside the topic folder when it is not the creator's own.
- Generic shots are fine here (flour falling, an oven light turning on). Results of a specific test are not: they stay with their piece, because they are evidence of that test.

## References

Other creators' covers, edits and formats, saved to study what works. Never published, never cut into a piece, never traced.

## Audio

- `find-video-audio` owns this folder: no sound goes into a piece without being prepared there and logged in `audio/log.md` with its source and license.
- The system sounds (the tap for labels, the soft whoosh, the list tick and the brand's C to E ding described in `../brand-guide/motion.md`) are fixed and repeat in every piece. Music changes from piece to piece.
- Keep only licenses that allow use in monetized social video without per-piece fees; record the exact credit text when the license asks for one.

## Working files

Analysis, frames, candidate sounds and test renders of a piece go in `../social/<piece>/edit/`, never here and never in a temporary folder.
