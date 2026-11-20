# Semantic sound catalog

What plays in each situation. Each entry gives the sound type, its character, the level relative to the voice, search terms (in English, which is how the catalogs are tagged) and when not to use it. Every sound is described in generic terms: the recognizable sound of a product, a platform, a film or a song belongs to someone else and is not searched for. Level parameters are starting points: what matters is that the sound feels part of the movement and never draws attention to itself.

## Brand motif (optional sound identity)

A brand can have a short motif that repeats, with different timbres, in the important sounds: two notes, the first short and the second 0.22 s later and sustained, which is the rhythm the generators in `scripts/` build. The two notes come from the "Sound identity" section of the workspace's `brand-guide/motion.md` and are passed to every generator; if the brand guide defines none, ask the user before inventing one. Rules:

- The notes never change; what changes is the timbre, the register and the duration depending on the sound. Transposition only if a whole piece uses music in another key and it clashes, and in that case it is noted in `piece.md`.
- It lives in the important moments: main emphasis hit, block transition and success. Never in the cut hit, the dry hit, the ticks or the pops. At most four appearances per video, or fewer if the brand guide's "Sound identity" sets a lower limit.
- Typical dressings: main emphasis hit (the motif as a synthesized low bass that takes its attack from the click of the brand's hit), block transition (the same tuned bass when an air riser lands, about 20 dB under the riser) and success (the motif on a bright marimba or bell). With those three the motif covers its moments; do not add more dressings without a piece-specific reason.
- Generators (they need numpy and ffmpeg; every option is written as a WAV plus a "0 ..." file with all of them in a row, for listening):
  - `scripts/tuned-hit-gen.py <output> <hit.wav> <options.tsv>`: the motif as a synthesized low bass with the hit's click on top (only the click is taken from the hit, not its body), in "joined" and "single hit" variants, each normalized to the same peak. `options.tsv`: `name<TAB>note1<TAB>note2` (notes such as E2, A2, F#2).
  - `scripts/motif-gen.py <output> <hit.wav> <level 0-1> <options.tsv>`: motif on a synthesized marimba, alone and over the hit. `<level>` is the motif peak relative to the hit peak (0.5 is 6 dB under it). `options.tsv`: `name<TAB>note1<TAB>note2[<TAB>gap<TAB>ring<TAB>vel1]`.
  - `scripts/synth-riser.py <output> <hit_without_motif.wav> <reference_riser.wav> <bass_dB> --notes <note1>,<note2>`: clean air and tonal risers that land on the motif (bass register, octave 2), next to a reference riser. `<bass_dB>` is the gain added to the motif bass: at 0 it peaks just under the riser, at -20 about 20 dB under it.
  - `scripts/transition-gen.py <output> <risers_folder> <hit_without_motif.wav> <bass_dB> <marimba_dB> --notes <note1>,<note2>`: the motif (bass register, octave 2) over every `.wav` riser of a folder. `<bass_dB>` works as in `synth-riser.py`; `<marimba_dB>` is the gain added to the marimba layer, which at 0 sits about 11 dB under the riser. It deletes the `.wav` files of `<output>` first.
  - `scripts/success-gen.py <output> --notes <note1>,<note2>`: the motif (high register, octave 5) in four bright timbres for the success sound.
  The scripts that read a hit need to know where its transient is inside the file. They assume 0.20 s from the start; for a hit with another layout add `--hit-at <seconds>`, or `--hit-at auto` to let the script find it (the first sample that reaches half of the peak) and print the value. They stop with a message if the file ends before the transient.

## System sounds (sound signature, fixed in the pool)

Each role has one fixed file chosen by the user, with the role written in the notes of its row in `media/audio/inventory.md`. If a role has no file yet, propose measured candidates for it before using one; if a piece needs another system sound, do the same.

| System sound | Use |
|---|---|
| Cut hit A and B | Shot cut and punch-in; alternate the two variants |
| Main emphasis hit | Hook, turn, payoff, reveal; carries the brand motif if there is one. Note in its inventory row where the hit lands inside the file |
| Dry emphasis hit | Figure or word mid-sentence |
| Entrance whoosh | Headline, screenshot, window, card coming in |
| Exit whoosh | The same element leaving; shorter and quieter, can be derived from the entrance one |
| List item tick | Each item of a list being built |
| Block transition | Block change and dynamic zoom; carries the motif if there is one. Note in its inventory row the instant of the landing, which is aligned with the moment the new block settles |

| Situation | Sound | Character | Level under the voice | Search | When not |
|---|---|---|---|---|---|
| Shot cut, punch-in | Short whip or dry thud, alternating A and B | about 240 ms, no tail, mid-dark tone with fast attack | at least 10 dB | "thud short", "soft impact", "camera punch", "sub hit short", "whip" | Never on a cut that does not change idea |
| Emphasis zoom | Low hit: main version with rise and tail, dry version for mid-sentence | Main about 1 s; dry about 0.3 s | 6 to 8 dB | "impact deep", "bass hit", "boom soft"; in humor, "comedy boom" | More than two per minute |
| Headline, card or screenshot entrance | Short whoosh | about 340 ms, ending where the movement ends | 8 to 10 dB | "whoosh short", "swish", "air whoosh", "wind whoosh" | If the element enters slowly, use a low slow whoosh or none |
| Element exit | Shorter and quieter whoosh | about 290 ms | 12 dB | "whoosh out short", "swish reverse" | If it exits with a fade, nothing |
| Block transition, dynamic zoom | Air riser that lands on the motif | about 0.75 s of audible rise plus the landing; align the landing with the end of the movement | 6 to 8 dB | "whoosh transition", "cinematic whoosh", "riser short" | One per block |
| List item being built | Short pop | about 280 ms with some body | 10 dB | "tick", "ui click soft", "pop short", "bubble pop" | Lists of more than five items: alternate tick and silence |
| Pill, label, pinned term | Soft pop | 80 to 150 ms | 10 to 12 dB | "pop soft", "ui pop", "bloop" | If a whoosh already played in the same second |
| Animated underline | Quick stroke | 150 to 250 ms, marker-like | 12 dB | "marker swipe", "pen stroke", "swipe short" | Optional; often better in silence |
| Figure counter | Brief ticking or roll | the counter's duration | 10 dB | "counter ticking", "slot tick", "number roll" | Small figures: only the final hit |
| Typed text appearing (a note, a message, a list, code) | Brief keys | 200 to 400 ms, 3 to 6 keystrokes | 10 to 12 dB | "keyboard typing short", "mechanical keyboard few keys", "typewriter keys short" | If the element already enters with a whoosh |

## Semantic sounds (change per piece)

| Situation | Sound | Search | Note |
|---|---|---|---|
| Money, price, cost, income, paying | Cash register, coin, payment chime | "cash register", "ka-ching", "coin drop", "coins", "payment success chime" | A generic chime, never the payment sound of a real platform |
| Error, mistake, something failing | Error buzzer, error beep, short glitch | "error buzzer", "wrong answer buzzer", "glitch short", "system error beep" | In an educational piece, a soft buzzer; a loud one only in humor |
| Success, a result that worked, a problem solved | The brand motif in a bright timbre if there is one; a generic ding if not, or if the piece already reached its motif limit | "success chime", "ding", "correct answer" | Short; counts toward the motif appearances per video |
| Notification, message, something arrived | Notification pop | "notification pop", "message tone", "ping" | A generic tone, never the notification sound of a real app |
| Reveal, surprising fact | Short riser plus hit | "riser short", "whoosh impact", "drum hit reveal", "dramatic sting" | The riser ends exactly on the hit |
| Comic turn, broken expectation | Record scratch, sad trombone, crickets | "record scratch", "sad trombone", "crickets" | Only humor or a self-aware turn |
| Sketch punchline | Comedy boom, a short deadpan reaction, music cut dry | "comedy boom", "bass drop short", "deadpan reaction" | One per sketch; the dry music cut needs no file |
| Waiting, loading, rendering, time passing | Clock, ticking, loading | "clock ticking", "loading", "elevator music short" (humor), "hourglass" | It lasts as long as the wait on screen |
| Thinking, doubt, "hmm" | Thoughtful "Hmm" | "thinking hmm", "crickets", "question mark sound" | Humor and light opinion |
| Alert, warning, risk | Brief alarm | "alert short", "warning beep", "alarm short" | Never a long alarm; only once |
| Speed, fast, accelerate | Long whoosh or engine | "fast whoosh", "speed up", "zoom by" | Goes with b-roll speed ramps |
| Writing, typing | Keyboard | "typing", "mechanical keyboard", "keyboard fast" | Under the voice; cut before it gets tiresome |
| Erase, delete, discard | Trash, swipe | "trash", "delete sound", "swipe away", "paper crumple" | Humor and demos |
| Grow, rise, improve | Short ascent | "rising tone", "level up", "sparkle rise" | Goes with arrows or figures going up |
| Fall, go down, lose | Short descent | "falling tone", "descending", "power down" | Comic turn or negative fact |
| Click, select, press in a demo | Interface click | "ui click", "mouse click soft", "button press" | One click per action shown, not per frame |
| Photo, screenshot, evidence | Shutter | "camera shutter", "screenshot" | When a screenshot appears as proof |
| Applause, celebration, community | Brief applause, cheers | "applause short", "crowd cheer short", "small crowd clap" | Only with a real reason |
| Laughter | Short human laughter | "laugh short", "small group laughing" | Punchline or humor reaction; never to laugh at someone nor as constant background laughter |
| Surprise, "wow" reaction | Audience "Ooh", reaction | "crowd ooh", "crowd wow", "surprised reaction" | After a figure or a result that deserves it |
| Comedy hit | Punch, bonk, slap | "cartoon bonk", "punch", "slap" | Only physical or sketch humor |
| Magic, something appearing | Sparkle, glint | "sparkle", "magic chime", "glitter" | When something appears "by itself"; not on every entrance |
| A machine or an automatic process at work | Processing beeps, text being typed on screen, short glitch | "data processing", "text readout", "computer beeps", "glitch short" | Avoid the robotic voice cliche except in a sketch |
| Drum roll before a reveal | Drum roll | "drum roll" | Ends right on the reveal |
| Start, round, "let's go" | Boxing or round bell | "boxing bell", "round bell" | Once, when the challenge or the comparison starts |
| Explosion, thunder, huge impact | Short explosion or thunder | "explosion short", "thunder crack" | Only for a very strong fact or turn; trim the tail |
| Silence as a device | Nothing | | In a sketch, holding the shot without sound is a joke; in an educational piece, the pause before the figure |

## Library folders

The default taxonomy of `media/audio/`, for a workspace that has no library yet. Adjust it to the workspace: a library that already has its own folders keeps them, and `media/audio/inventory.md`, with one heading per folder, is the list that counts. Create a new folder only when no existing one fits. The detail of each file (duration, origin, notes such as "sketch only") is in the inventory.

SFX (`media/audio/sfx/<type>/`): `whoosh-and-transitions`, `hits-and-impacts`, `risers`, `snaps`, `pops-and-bubbles`, `strokes-and-sweeps`, `interface-keyboard-screenshot`, `money`, `error-and-denial`, `success-and-bells`, `notifications-and-calls`, `suspense-and-reveal`, `alert-and-waiting`, `celebration-and-start`, `reactions-and-surprise`, `thinking-and-doubt`, `laughter`, `generic-comedy`, `pass-bys-and-speed`, `paper`, `explosions`.

Music (`media/audio/music/<mood>/`), one folder per mood: `light`, `bright-neutral`, `with-pulse`, `minimal`, `optimistic`, `dramatic`, `comic-and-cliche`.

## Where to look in the library

| Situation | Folder |
|---|---|
| Shot cut, punch-in, emphasis zoom | `sfx/hits-and-impacts` |
| Element entrance and exit, block transition | `sfx/whoosh-and-transitions`, `sfx/risers` |
| List item, pill | `sfx/snaps`, `sfx/pops-and-bubbles` |
| Animated underline | `sfx/strokes-and-sweeps` |
| Figure counter, typed text, click, screenshot, machine at work | `sfx/interface-keyboard-screenshot` |
| Money | `sfx/money` |
| Error | `sfx/error-and-denial` |
| Success (the brand motif first, if there is one), rise, magic | `sfx/success-and-bells` |
| Notification, message | `sfx/notifications-and-calls` |
| Reveal, drum roll, suspense | `sfx/suspense-and-reveal` |
| Alert, waiting | `sfx/alert-and-waiting` |
| Applause, celebration, start bell | `sfx/celebration-and-start` |
| Surprise, disbelief ("wait, what?") | `sfx/reactions-and-surprise` |
| Thinking, doubt, realizing | `sfx/thinking-and-doubt` |
| Laughter | `sfx/laughter` |
| Comic turn, going down or losing, crickets, generic punchline | `sfx/generic-comedy` |
| Speed | `sfx/pass-bys-and-speed` |
| Erase, discard | `sfx/paper` |
| Explosion, thunder | `sfx/explosions` |
| Music bed | The `music/<mood>` folder closest to the "Character" column of "Music by format"; cliche music for a joke in `music/comic-and-cliche` |

## Music by format

The formats are the workspace's own (`editorial/`); these rows are common ones. Use the closest row and say which one was used.

| Format | Character | BPM | Instrumentation | Level |
|---|---|---|---|---|
| Educational with rhythm | Neutral, bright, no leading melody | 85 to 110 | Soft keys, discreet electronic pulse, no heavy drums | 20 dB under the voice, rises in gaps |
| Demo (a tool, a product, a technique) | Restrained, with pulse | 95 to 120 | Clean synths, light percussion | 20 dB under the voice |
| Opinion | Minimal or none | 70 to 90 if any | Pads, distant piano | 22 to 24 dB under the voice |
| Progress log (a build in public, a challenge, a behind-the-scenes series) | Optimistic, with forward motion | 100 to 120 | Guitar or keys with pulse | 20 dB under the voice |
| Sketch | Whatever the premise asks for; can be cliche on purpose | free | the joke's (soap opera, suspense, epic) | 16 to 18 dB under the voice, and cut dry at the punchline |
| Dense explanation, sensitive topic | None | | | |

## Freesound search terms

Useful filters: `license:"Creative Commons 0"` for CC0; `duration:[0.1 TO 1.5]` for system SFX; `duration:[20 TO 120]` for beds; `tag:loop` for loops; `type:wav`. Sort by `rating_desc` or `downloads_desc` and always have the top three results reviewed by listening.
