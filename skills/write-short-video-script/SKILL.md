---
name: write-short-video-script
description: 'Write the full spoken script of a short vertical video (Instagram Reel, TikTok, YouTube Short or LinkedIn video, from 15 seconds to 3 minutes) designed to hook and retain without sounding frantic. Before writing, it always asks the user what decides the script, presents a plan (angle, payoff, hook candidates, beats) and waits for explicit approval. Then delivers `social/YYYY-MM-DD-slug/script.md`: hook chosen with recommend-video-hook, promise, beats chained by causality, re-hooks, payoff of the promise, CTA and final cut, with beat map, on-screen text, visual changes with a purpose, delivery notes and, when the user asks for it, a table for recording clip by clip. Covers educational talking head, tool or product demo, opinion, build in public, humor sketch and visual video (motion graphics with no creator on camera, with voice-over or without voice, such as an announcement or a figure). Use whenever the user asks for a script, "what do I say in this Reel", to turn an idea, an article or a piece of research into a short video, to rewrite a boring script or to structure a sketch. Do not use for long YouTube videos, captions (write-caption) or carousels.'
---

# Write Short Video Script

A short script that hooks is not a script with more cuts. It is a script where each sentence makes the next one necessary, the hook's promise is kept and the person who arrived scrolling finishes the video with something they did not have. This skill writes that in the creator's voice, as the brand's voice guide describes it, with humor that shows up because the situation has it and a rhythm that comes from new information, not from the editing.

Write everything the user reads (chat, questions, `script.md`) in the user's language, or in the one the workspace instructions set. The spoken script is written in the language the video will be recorded in.

The structure, lengths and cadences in this skill are recommendations to start from, and its style rules are defaults: the brand guide and the workspace instructions win when they say otherwise, and the account's own retention data corrects any figure here. Budgets counted in words assume a language written with spaces between words (`references/pacing.md`).

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| `recommend-video-hook` skill | Yes | Producing the hook candidates the plan shows, among which the user chooses | Install the `recommend-video-hook` skill from the ai-skills repo |
| `brand-guide/voice-and-humor.md`, `brand-guide/audiences.md` | No | The creator's voice, humor and spoken register; who the video is for | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/` there has filled-in examples at the same paths |
| `editorial/pillars.md`, `editorial/<channel>.md` | No | The pillar the idea serves; the channel's length, register and rules | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/editorial/` there has filled-in examples |
| `operations/research-policy.md`, `operations/review-and-approval.md` | No | What must be verified before stating it; what needs the user's approval | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/operations/` there has filled-in examples |
| `brand-guide/visual-ideation.md` | No | The method of the visual ideation offered before filling the beat map's "Visual" column; without it, the ideation follows step 6 of "Write" | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/visual-ideation.md` there is a filled-in example |
| `editorial/series/<series>/series.md` | No | The intro and the visual kit, when the piece belongs to a series | Write it following `CONVENTIONS.md` in the ai-skills repo |
| `social/index.md` | No | Not repeating recent ideas or structures | Grows as pieces are approved; format in `CONVENTIONS.md` in the ai-skills repo |
| A timed transcript of an earlier video by the creator (`social/<piece>/edit/analysis/final-video/transcript.srt` or `source/recording/transcript.srt`) | No | Budgeting words with the creator's real pace (step 8 of "Design the backbone" says what to do without it) | Produced by `analyze-video` on an earlier video |
| `analyze-video` skill | No | Transcribing a recording the user shares before writing on top of it | Install the `analyze-video` skill from the ai-skills repo |
| `research-content-topic` skill | No | Researching technical claims, figures, versions or news before the plan; without it, check them against current sources with the agent's web tools | Install the `research-content-topic` skill from the ai-skills repo |
| `generate-ai-images` skill | No | AI raster images the beat map needs | Install the `generate-ai-images` skill from the ai-skills repo |
| `edit-short-video` skill | No | The visual rules the beat map follows, in `edit-short-video/references/visual-system.md` (visuals around the creator, interface zones, key phrases) and `edit-short-video/references/visual-video.md` (the scenes of a visual video); without it, use the figures given in this skill | Install the `edit-short-video` skill from the ai-skills repo |
| `write-caption` skill | No | The caption, written from the final video; this skill never proposes one | Install the `write-caption` skill from the ai-skills repo |
| The agent's structured question tool | No | The questions and approvals of the gate (`AskUserQuestion` in Claude Code); without one, ask in the chat with the full text in view | Part of the agent |
| A web search or reading tool | No | Checking claims, figures, versions and news against current sources before the plan; without it, mark them as pending and ask the user for the source | Part of the agent |
| Workspace skills for a GIF search, a brand review or a public-text check | No | Reaction assets, the review of a sensitive piece and the mechanical check of the text; each is used only if the workspace has it | Whatever the workspace provides |

## Load context

Read the workspace files of the table that exist, for what each one is used for.

Read this skill's references according to the piece:

- `references/structures.md`: anatomy of the short script and variants by format (educational, demo, opinion, build in public, sketch, visual video), re-hooks and CTAs.
- `references/pacing.md`: word budget by length, speaking pace, the on-screen text budget of a visual video without voice, visual cadence, what is over-editing and what is dynamism.
- `references/platforms.md`: limits, signals and rules of Instagram, TikTok, YouTube Shorts and LinkedIn, with their verification date. Verify before stating a platform fact in public.

## When to invoke other skills

- **Hook:** the hook is chosen once, inside the plan. When the user has answered the questions of the gate and the payoff is defined, invoke the `recommend-video-hook` skill through the skill tool and follow its flow; reading only its `SKILL.md` does not count as invocation. The plan shows all its candidates with its recommendation marked, and the user chooses one when approving the plan. That hook is the first line of the script; it is not invoked again after the approval. If the payoff changes while writing the body, the approved plan no longer holds: go back to the gate with the new payoff.
- **Existing video or audio:** if the user shares a recording (an already shot sketch, a live, a demo), invoke the `analyze-video` skill to transcribe and understand the shots before writing on top of it.
- **AI raster image:** invoke the `generate-ai-images` skill. For GIFs, memes or reaction assets, use the workspace's GIF search skill if it has one.
- **Caption:** written by the `write-caption` skill from the final video; the script does not propose it.
- **High-impact review:** before considering a sensitive piece, a strong-opinion piece or one with technical claims ready, run the workspace's brand review skill if it has one; otherwise review against the voice guide and the research policy yourself and say so.

## Define the piece

1. **One idea and one transformation.** What the person will understand, question or be able to do when they finish. If there are two ideas, there are two videos.
2. **Format:** educational talking head, demo, opinion, build in public, sketch or visual video (the creator is not on camera: motion graphics scenes, with their voice-over or without voice). The format decides the structure (see `references/structures.md`).
3. **Platform and target length.** The platform is the one the user names or the workspace's channel guides set; when neither says, write for Instagram and note what changes for the others (`references/platforms.md`). Length by intent, as a starting recommendation: 30 to 60 seconds for an educational idea, 45 to 90 for a demo with screen, 15 to 45 for a sketch or a visual video, 15 seconds to 2 minutes on LinkedIn. Instagram does not recommend videos longer than 3 minutes to non-followers. Every extra 15 seconds must be justified with new information.
4. **What is true.** What the creator tested, which figure is verified, which anecdote exists. Do not invent experiences, results, emotions or tool usage. If the argument needs an experience that is not documented, ask for it or write without it.
5. **Research first** if the video has technical claims, figures, versions, comparisons or news, before proposing the plan. The agent's knowledge is a starting point; whatever might be wrong or might have changed is checked against current sources according to the workspace research policy (or with the `research-content-topic` skill).
6. **The account's data.** If there are retention curves from earlier pieces (Instagram Insights, YouTube Studio), ask for them or consult them: they say at which second this audience leaves, which is worth more than any general rule. Quick reading: drop in the first 3 to 5 seconds, hook problem; drop later, script problem or broken promise.

This stage does not end with stated assumptions: it ends with the user's agreement, at the next gate.

## Agree with the user before writing

Mandatory gate. Do not write the script until the user has approved the plan; the only lines written before that are the payoff and the hook candidates the plan shows. A short brief or a loose idea ("I want to talk about the event") is never enough to skip it.

1. **Ask.** Use the agent's structured question tool (`AskUserQuestion` in Claude Code), several questions in a single call when they are independent, with concrete options and room for a free answer. Ask at least what decides the script:
   - What they want the person to take away at the end (the transformation) and what the creator wants to say in their own words.
   - What format and register they want (educational, demo, opinion, build in public, sketch, visual video; serious, light, mixed) and, when it is a visual video, whether the creator narrates it.
   - What is true and what material exists: facts, figures, real anecdotes, b-roll, screen.
   - Length and platforms.
   - If the user proposed a hook or a line, whether they want to keep it literally, use it as a starting point or open it to alternatives.
   If the brief already answers any of these, do not repeat it; ask what is missing. If the user rejected an earlier script for the same piece, first ask what did not work (angle, tone, length, structure, facts) before proposing something else.
2. **Propose the plan.** With the answers, present in the chat a short plan, not a script:
   - Central idea and transformation in one line.
   - Format, platform(s), length and word budget.
   - Payoff written word for word.
   - The hook candidates, as `recommend-video-hook` delivers them in the chat (all of them, ranked, each with its template, spoken line, frame 0 and score, and the recommended one marked), for the user to choose one. If the user asked to keep a hook of their own literally, show it scored next to the others.
   - List of beats with their connector ("but" / "therefore") and the example or material each one carries.
   - Proposed CTA and planned humor moments.
   - Facts that will be stated and which ones are still to be verified.
   If there are two reasonable angles, present both in that same format and recommend one.
3. **Ask for explicit approval** with the structured question tool, once the whole plan and all the hook candidates are in the chat: which hook the user chooses, and whether they approve the plan, approve it with changes (and which ones) or want it redone. Iterate the plan as many times as needed. Only with the plan approved do you move on to the backbone and to writing.
4. **Record the agreement** in the "Agreed plan" section of `script.md` (angle, payoff, chosen hook, beats and the user's decisions), so a later review knows what was agreed. The chosen hook is recorded as `recommend-video-hook` defines in "Record the choice": the line `- Hook: <code> <template name>: "<spoken line>"` in the "Hook" section of `script.md` and at the top of `hooks.md`.

## Design the backbone

Only with the plan approved. Before writing a single spoken line:

1. **Payoff.** The line that delivers what the hook promised: what the person takes away, word for word as approved in the plan. The script is built backwards from there.
2. **Hook.** The one the user chose in the plan, with the card `recommend-video-hook` produced for it. The hook is the open promise of the payoff.
3. **Promise or preview (about seconds 3 to 8).** One sentence that says what they will see or understand, or that anticipates the conflict. No "in this video". Early on, as a recommendation before second 10, there has to be proof that the promise is real: a data point, a before and after, a piece of the result, a mini demo. Promising without showing anything until the end reads as clickbait.
4. **Beats.** List the body's beats. Between every two beats "but" or "therefore" has to fit. If "and then" fits, the beat is unnecessary or in the wrong order. A 60-second Reel allows hook, promise, two or three beats with an example, payoff and CTA; no more.
5. **Re-hooks.** Mark one about every 15 to 20 seconds, as a starting recommendation that the account's retention curves correct (`references/structures.md`): a new question, a twist, a concrete example, a change of register (from explanation to mental image, from serious to comic observation), a demonstration. Halfway through the video, restate the premise in one line because many people have just arrived.
6. **CTA.** By default one, in one sentence, right after the payoff, and the video ends with it; a brand guide that closes its videos another way (no CTA, a fixed sign-off) wins. Specific and honest: "send it to someone who is about to try this", "save it for when you try it", a question the creator really wants to answer. Do not ask to "comment a word" or "wait for the end": Instagram treats it as engagement bait.
7. **Ending.** By default the payoff, the CTA and a hard cut, with no "and that's it", no goodbye, no outro and no logo, unless the brand guide defines a closing.
8. **Word budget.** Take it from `references/pacing.md`. If there is a timed transcript of an earlier video by the creator (`social/<piece>/edit/analysis/final-video/transcript.srt`, or `source/recording/` in pieces not yet edited), calculate their real pace in words per minute and budget with that figure. If not, aim for the center of the range and deliver an ordered list of cuts in case they speak more slowly; the payoff is never cut.
9. **Several platforms.** A single backbone. If the second platform only changes the hook, the CTA, a few lines or the specs, deliver an "Adjustments for <platform>" block with those differences. If more than a third of the script changes, deliver a full script and map per platform.

## Write

1. **Write to be spoken.** One idea per sentence, verbs, second person without overdoing it, sentences said in one breath. Read aloud: if a sentence needs an odd breath or sounds like a read article, simplify it.
2. **No preamble.** No greeting, introduction or context before the hook. The essential context comes in after the promise, in one sentence. A standalone piece has no intro. If the piece belongs to a series or show and the series plan (`editorial/series/<series>/series.md`) defines an intro, all its episodes carry it right after the hook, with the exact text of the plan; if the plan does not define one, there is no intro. That decision is made when designing the series, not in each script.
3. **Concrete before abstract.** Each idea with an example that can be seen or imagined: the object, the mistake, the screen, the result, the everyday situation. Showing while you explain retains more than explaining and then showing.
4. **Stance.** The script takes a position and backs it with evidence. Separate fact, inference and opinion when there could be confusion. Add the nuance or limit that avoids a misleading conclusion.
5. **Humor with a purpose.** Apply the voice guide: no minimum or maximum quota; several light beats if they get to the value fast; variety of devices (observation, controlled exaggeration, mental image, pause, expression, on-screen text, reaction, callback); one playful moment at a time, not several in a row; reduced in warnings and precision explanations. If, after removing the jokes, any creator in the niche could sign the script, the voice is not there.
6. **Visuals with ideation, around the creator.** As a general rule, the creator is on camera and the visuals happen around them, with visual-only moments when they add something (`edit-short-video/references/visual-system.md`): the beat map indicates where each visual appears relative to them. Do not mark looks or gestures unless asked. In a visual video the creator is not on camera and the visuals are the piece: each beat is a scene with one lead visual that acts (`edit-short-video/references/visual-video.md`), its words are meant for the eye, a single idea on each screen, and it carries the whole story when nobody speaks, or only what is not spoken when the creator narrates. Before filling the "Visual" column of the beat map, offer a visual ideation (`brand-guide/visual-ideation.md` when the workspace has it); the user decides. If they ask for it, explore 6 to 8 directions from different categories, look for a visual world that unifies the video (and that makes use of what is already in the script), show all the directions in the chat and record the chosen one in the beat map. If the piece belongs to a series, start from its visual kit.
7. **Dynamic but not too much.** The rhythm comes from the density of new information and from the causality between beats. As a recommendation (`references/pacing.md`), mark a visual change with a purpose every 5 to 10 seconds (example on screen, term pinned in text, change of framing when the beat changes, demo), and hold the shot when the explanation demands precision. No cutting for the sake of cutting, constant zooms, sound effects or flashes. Rhythm in waves: fast hook, development that breathes, fast peak and a close that ends on a hard cut.
8. **The creator's spoken register.** Write in the creator's own voice, as the voice guide describes it. Keep each term in the form the audience says and searches for, and explain it in half a sentence if it could exclude part of the audience.
9. **Leave room.** Hook and payoff written word for word because they are the seconds that decide; the body in sentences the creator can say their own way. Do not choreograph every second unless asked.

## Review before delivering

- **Promise:** the hook promises exactly what the payoff delivers. Point out the beat where it is kept and the proof that appears before second 10.
- **Silence:** the first three seconds are understood without audio thanks to the first frame and the on-screen text.
- **Causality:** count the implicit "and then" between beats. There must be zero.
- **Budget:** words within the range of the target length; when the piece is a visual video with no voice, on-screen text within the reading budget of `references/pacing.md`.
- **Ending:** the payoff comes first and the close the piece uses follows it (by default one CTA in one sentence); there is no goodbye.
- **Truth:** no invented anecdote, figure, emotion or tool usage; claims with a source or marked as pending.
- **Verification with the user:** every pending item only the user can resolve (confirming a figure or a fact, choosing between two wordings, providing a concrete case, authorizing a mention) is asked with the structured question tool as soon as the script is written, with concrete options and the option of a free answer. Do not deliver a list of pending items expecting the user to read and answer it on their own. The answers are applied to `script.md` before considering it delivered.
- **Voice:** newspaper test (without jokes it still sounds like the creator), humor distributed, no guru, no hype, no "this changes everything".
- **Mechanics:** the punctuation and style rules of the brand's voice guide, and no invisible characters or exotic spaces (run the workspace's public-text checker if it has one); emojis only in on-screen text or caption and only if they reinforce a line that already works.
- **Platform:** length within what is recommended; on-screen text inside the safe zone given in `references/platforms.md`; the creator's own material, or added value if reacting to someone else's.

## Deliver

The deliverable is always a Markdown file, never just text in the chat. Each script creates its own piece folder inside `social/`, even if the piece does not yet have a record, cover or approval:

```
social/YYYY-MM-DD-slug/
  script.md
  hooks.md
  source/
    recording/   the creator's on-camera takes, or their voice-over recording (and the transcript when it exists)
    broll/       everything else: support clips and photos
```

- The date is the day the script is started; the slug is short, describes the piece and not the channel (see `CONVENTIONS.md`). If the user already has a folder for the piece, use it.
- When creating the piece folder, also create `source/` with its two empty subfolders, `recording/` and `broll/`, at the same moment, so the user can drop the take in one and the support clips and photos in the other as soon as they record. The other subfolders (`edit/`, `export/`, `cover-src/`) are created when they are used.
- One script per folder. A new version of the same script overwrites `script.md`; a different idea is another folder.
- `hooks.md` holds the hook candidates the plan showed, in the format of the "Deliver" section of `recommend-video-hook`, headed by the `- Hook:` line of the chosen one. It is saved now because the piece folder did not exist when the candidates were shown.
- `script.md` contains the full deliverable with the template below, headed by a working title and a status line (`draft`, `reviewed` or `approved for recording`).
- In the chat, answer with the file path, the chosen hook and the word count. After every change the user asks for, show in the chat the full updated script (not only the changed lines) with its word count and length, always in the unified format: for each beat, with its time, **Say** (exact text), **On screen** (visual around the creator) and **Sound**. In a visual video each beat is a scene and carries **Voice-over** (word for word, when the piece is narrated), **On-screen text** (exact text), **On screen** (the lead visual and what it does) and **Sound**. While the visuals or sound of a beat are not defined, that line says "to be defined". It is also the format of the "Unified script" section of `script.md`. Verifications that depend on the user are done with the structured question tool in that same turn, never as a list for them to read later.
- **Script for recording.** Recording clip by clip is one method the user may choose: the creator records each sentence, or each short group of sentences, as its own clip and repeats it several times so the best take can be picked later (`analyze-video` supports it as sentence-by-sentence recording). A creator who records the whole script in one take, or in sections, does not need this table. When the user asks for the script for recording, deliver it in the chat and in the "For recording" section of `script.md`:
  - A table with **Clip** (two digits, in order), **Part** (Hook, Intro, B1, B2…, Payoff, CTA), **Sentence** (exact text of the script, without changing words) and **How to say it** (intonation and delivery in a few words), with the intonation marked as **open** (the sentence continues in the next clip and the voice does not close) or **closes** (full stop).
  - Each clip is said in one breath: it is cut at the period, semicolon or comma where the idea breathes, like "Weigh the flour instead of scooping it with a cup;" and then "the bread comes out the same every time.". If a clip is still long, suggest below the table how to split it.
  - The pauses the edit asks for (the silence for a sound effect), any closing gesture and the reactions after a sentence, with their length ("a second and a half looking at the camera"), go in "How to say it" of their clip, so the edit keeps them.
  - Above the table, remind the creator of one second of silence looking at the camera before and after each repetition: that way `analyze-video` separates the takes by their silences and the cut does not show the face changing.
- **A visual video has no recording table.** With no narration, nobody records anything: the "Screens" section of `script.md` takes its place, one row per scene with its exact text and its lead visual, and it is what `edit-short-video` builds from. With voice-over, the "Spoken script" section is the text to read: the creator records it as one audio file, read in one go, repeating a sentence when it goes wrong after a second of silence, close to the microphone in a quiet room, and saves it in `source/recording/`. The takes flow of `analyze-video` measures the face and does not apply to a voice recording.
- The "Pending verification" section of the file records what was verified, with which source, and what the user answered to each question. Only what neither of you can resolve yet remains pending (for example, a figure that does not exist yet), with who will resolve it and when.
- The piece record (`piece.md`), the cover and the line in `social/index.md` are created when the user approves the caption or cover; the record links `script.md` on its `Source` line and carries the `- Hook:` line in its header.

The `script.md` template (translate the headings into the user's language):

```markdown
# <Working title>

- Status: draft | reviewed | approved for recording
- Date: YYYY-MM-DD

## Agreed plan
<angle, payoff, chosen hook, beats and decisions the user approved before writing, with the approval date>

## Concept
- Format, platform(s) and target length (budget: N words)
- Audience and transformation
- Payoff

## Hook
<the line `- Hook: <code> <template name>: "<spoken line>"`, then the card of the chosen hook as recommend-video-hook delivered it: second line, first frame, on-screen text, delivery, where it is paid off; the two next best candidates and the hook's risks summarized in one line each>

## Spoken script
<full text for camera, with discreet beat marks in brackets, for example [B2], and no editing instructions inside the text; in a visual video, the voice-over text, and without voice this section is left out>

## For recording
<only when the user records clip by clip: table Clip | Part | Sentence | How to say it, with open or closes intonation; see "Script for recording" above. Left out in a visual video>

## Screens
<only in a visual video: table Scene | Beat | On-screen text (exact) | Lead visual and what it does | How it arrives (from behind or from the side) | Sound. Without voice, also the characters of each text and the seconds the screen needs, from `references/pacing.md`>

## Unified script
<the full script by beat, with its time: **Say** (exact text), **On screen** (visual around the creator) and **Sound**; in a visual video, **Voice-over** (if any), **On-screen text**, **On screen** and **Sound**; "to be defined" while undecided. Headed by the chosen visual world and the recording notes>

## Beat map
| Approx. time | Beat and function | What is said | Visual | On-screen text |
|---|---|---|---|---|
| 0-3 s | Hook (template) | summary of the line | ... | ... |
| 3-8 s | Promise | ... | ... | ... |
| ... | B1 / Re-hook / Payoff / CTA | ... | ... | ... |

The "On-screen text" column only carries what the voice does not say (a figure to pin in the hook, a credential, a date, a data point, a visual joke); burned-in subtitles already cover what is spoken, so most beats leave it empty. Exception: the key phrases highlighted with animated typography, one every 20 to 25 seconds (two or three in a one-minute Reel: the hook, the central idea and, if it deserves it, the punchline), marked in that column as "Key phrase" (`edit-short-video/references/visual-system.md`). When a visual video has no narration, every word of the story goes in that column.

## Adjustments for <other platform> (only if applicable)

## Delivery and editing
- Pauses, expressions, framing changes with a purpose, humor moments that depend on delivery
- Assets approved or to find (GIF, meme, screenshot, diagram)

## Pending verification
- Verified: claim, source and date
- Confirmed by the user: question asked, answer and date
- Truly pending: what is missing, who resolves it and when
```

Total words of the spoken script at the end of the script block; for a visual video with no narration, the total of its on-screen text instead. Do not mark the script as ready to record until the technical and editorial review and the user's review are complete. This skill does not publish or schedule anything.
