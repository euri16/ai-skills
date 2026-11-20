---
name: recommend-video-hook
description: 'Recommend the hook of a short vertical video (Reel, TikTok, Short or LinkedIn video): the first spoken line, the first frame and the on-screen text of the first 3 seconds. Covers pieces with the creator on camera and visual videos (motion graphics with voice-over or without voice, whose hook is the first frame with its headline). Starts from an idea, a brief or a script; writes 12 to 15 candidates with proven templates (a library of hook templates and the hook references the user keeps in the workspace), scores them with a rubric and returns them all ranked, with a main recommendation that has template, frame 0, on-screen text, exact line, how to say it and the point of the video that pays it off. Use whenever the user asks for a hook, an opening, a first line or "how do I start this video", wants to improve a weak opening, choose between several hooks or check whether a hook is honest or worn out; also when another script skill needs to set the hook before writing. Does not write the full script (that is write-short-video-script).'
---

# Recommend Video Hook

A hook is a three-second promise that the video pays off later. This skill chooses what to promise and how, so that the person scrolling stays and, at the end, feels the video gave them what the opening announced. It does not look for the most aggressive hook; it looks for the one the creator can deliver on and would say on camera without playing a character.

Write everything the user reads (chat, questions, files), including every hook, in the user's language or in the one the workspace instructions set. Hooks are written in the language the video will be recorded in.

The lengths, counts and thresholds in this skill are recommendations to start from, not measured laws, and its style rules are defaults: the brand guide and the workspace instructions win when they say otherwise. The lengths counted in words assume a language written with spaces between words.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| The idea, brief or script of the piece (`social/<piece>/script.md` when it exists) | Yes | Finding the payoff the hook promises | Share it in the chat, or write the script with `write-short-video-script` |
| `brand-guide/voice-and-humor.md` | No | Lines the creator would say on camera without playing a character | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/voice-and-humor.md` there is a filled-in example |
| `brand-guide/audiences.md` | No | Who the video is for (step 5 of "Understand the piece" says what to do without it) | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/audiences.md` there is a filled-in example |
| `editorial/<channel>.md` | No | The channel's register and rules | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/editorial/` there has a filled-in channel guide (`instagram.md`) |
| `editorial/hook-references.md` | No | Hooks from creators the user likes, which take priority over the general templates; without it, only the library is used | Copy this skill's `assets/hook-references-template.md` to `editorial/hook-references.md` in the workspace; the skill adds rows as the user shares references |
| `social/<piece>/piece.md` | No | The piece record, whose header receives the `- Hook:` line of the chosen hook | Created when the piece is approved; fields in `CONVENTIONS.md` in the ai-skills repo |
| `editorial/series/<series>/series.md` | No | Whether the piece belongs to a series with an intro, which the hook has to leave room for | Written when the series is designed, following `CONVENTIONS.md` in the ai-skills repo |
| `operations/research-policy.md` | No | What has to be verified before a data hook states it; without it, every figure in a hook needs a source the user accepts | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/operations/research-policy.md` there is a filled-in example |
| The agent's structured question tool | No | Asking the user to choose the hook (`AskUserQuestion` in Claude Code); without one, ask in the chat with every candidate in view | Part of the agent |
| A web reading tool | No | Opening an article, a guide or an account the user shares as a hook reference; without it, ask the user to paste the text | Part of the agent |
| `social/index.md` | No | Not repeating the template of the three previous pieces (its `Hook` column) | Grows as pieces are approved; format in `CONVENTIONS.md` in the ai-skills repo |
| `analyze-video` skill | No | Transcribing a reference video the user shares; without it, ask the user for the first line and describe frame 0 from what they say | Install the `analyze-video` skill from the ai-skills repo |

## Load context

Read the workspace files of the table that exist.

The unit this skill chooses, rotates and records is the **template**: one of the hook mechanisms of `references/hook-templates.md`, each with a code and a name (for example `C4` X versus Y). To know which templates the three most recent pieces used, read the `Hook` column of `social/index.md`, which stores the code; if a row has none, read the `- Hook:` line of that piece's `piece.md`, and if there is none either, deduce the template from the cover concept and the central idea.

Always read `references/hook-templates.md` (the templates: mechanism, when each one fits, example and risks, plus the templates natural to each format) and `references/hook-library.md` (spoken formulas for each template, visual devices and the scoring rubric). If the workspace has `editorial/hook-references.md`, read it too: the hooks from creators the user likes take priority because they reflect the brand's taste. Read `references/evidence.md` to justify a decision or settle a doubt about honesty, platform, metrics or fatigue.

If the user shares a video, an account, an article or a guide as a hook reference, add it to `editorial/hook-references.md` before proposing, as that file's instructions say. If the file does not exist, create it from `assets/hook-references-template.md`. References are never saved inside this skill's folder, which is replaced when the skill is reinstalled.

## Understand the piece

Before proposing anything, pin down in one or two lines:

1. **Central idea and payoff.** What the video actually delivers: a result, a data point, a method, a twist, a stance. If the material does not make the payoff clear, ask the user or deduce it from the script and state it. A hook without an identified payoff is potential clickbait; in that case the hook changes, the video does not get inflated.
2. **Format:** educational talking head, tool or product demo, opinion, build in public, humor sketch or visual video (motion graphics with no creator on camera, with voice-over or without voice). Each format has natural templates (table in `references/hook-templates.md`). When a visual video has no narration, nothing is spoken: its hook is the first frame and the words on it, so the "spoken line" of each candidate is the headline that is read and the "second line" is the text that follows it on that screen. When it is narrated, the spoken line is the sentence that opens the narration, and frame 0 is the first scene.
3. **Platform and length.** Instagram asks that the first 3 seconds hook and only recommends videos of 3 minutes or less to non-followers; TikTok asks for the proposition in 3 seconds and the hook within 6; YouTube measures whether people "stayed to watch" past the first seconds; LinkedIn asks for 3 seconds and a professional audience. The same hook usually works for all four; change the on-screen text or the register when it does not.
4. **What is true.** What the creator tested, which figure is verified, which experience exists. The hook can only rest on that. Do not invent results, anecdotes, credentials or emotions.
5. **Audience.** Take it from the brand's audience file. If there is none, ask who the video is for before writing.

Ask only if the answer materially changes the hook (for example, if it is unknown whether there is a visual result to show). In all other cases, state the assumption and move on.

## Choose the hook

1. **Start from the payoff.** Write in one line what the person will have at the end. The hook is the open version of that line.
2. **List the piece's angles.** The same topic hooks from different places: the pain the person lives, what they spend or lose, what they can save or gain, what they believe and is not so, a news item or well-known figure, a surprising data point, a comparison, a test that can be done on camera. Note 4 to 6 angles before writing lines.
3. **Visual first.** For each angle, decide what is seen in frame 0 and what on-screen text sums it up, with devices from the library (mid-action, object or result on screen, split screen, visual "wait", before and after). As a recommendation, the on-screen text of a hook has 3 to 5 words and stays under 8, so it is read in the first second; this is the length every other mention of the hook's on-screen text refers to. The headline of a visual video without voice is the hook line itself and may run to 8 words. The spoken line is written afterwards and names the same thing that is seen and read. Never a neutral face with no text or context, never a logo (nor, when there is no camera, a title card or an empty background).
4. **Write 12 to 15 candidates** with at least 6 different templates, using the spoken formulas of `references/hook-library.md` and prioritizing the structures in `editorial/hook-references.md` when they fit. Each candidate has its template (code and name), a spoken line, a second line, frame 0 and on-screen text. Copy structures, never the content of the examples: the content comes from the payoff and the verified facts of the piece. Look for the hyper-specific, concrete detail before the general version.
5. **Score with the rubric** in `references/hook-library.md` (eight criteria from 0 to 2). Only recommend what scores 13 or more and never one without an open unknown. If none reaches it, write more candidates from other angles rather than lowering the bar.
6. **Filter with brand judgment.** Well-known formulas are allowed ("Nobody tells you…", "Stop doing…", "I tested it so you don't have to…", "POV:"). Discard generic execution (no concrete subject, no real data, no contrast), the promise the video does not keep, unverified figures, anecdotes or experiments the creator did not live, hype with nothing to show ("this changes everything") and asking for interaction as an opener ("comment X if...").
7. **Check fatigue.** Do not recommend a template that any of the three previous pieces used if another one scores equally high.
8. **Silent test.** The first three seconds without audio: if it is not clear what it is about, on-screen text or an image is missing.
9. **Payoff test and early proof.** Point out where the hook is paid off and which part of that proof appears before second 10 (a data point, a before and after, a piece of the result, a mini demo). If the piece belongs to a series with an intro, that proof has to fit in the hook itself, before the intro. In a sketch, decide between dramatic irony (premise visible from the start) and reveal (something hidden until the punchline); in 30 seconds dramatic irony almost always wins.
10. **Leave something open.** The hook opens a question, an unknown or a tension that the video closes later; a statement that already carries its answer does not hook. The second line amplifies the unknown or makes it personal ("and you probably do it every morning"), never resolves it. If the piece belongs to a series with an intro, the unknown has to stay open during the intro.
11. **Write to be spoken.** As a recommendation, a first line of 3 to 10 words, affirmative rather than a roundabout question, no greeting, no "in this video", no opening filler, no jargon in the first line. Also write the second line, the one that amplifies or turns the hook into a concrete promise. A question only works if the person answers it alone or the answer arrives right away, within a couple of seconds.

## Deliver

**In the chat, all candidates and only what is needed to choose.** The user chooses among everything that was generated, not among a preselection: show the 12 to 15 candidates, sorted by score, each with its template (code and name), the spoken line (and the second line), what is seen in frame 0 in a few words and the score. Mark the recommended one and say why in one sentence. Nothing else: no reading of the piece, no delivery, no risks. If a hook depends on something that has to be verified or obtained (a screenshot, a figure), say so in half a line next to that hook. Never ask which one to choose without having shown them all in the chat first.

**In the file, all the detail.** If the piece already has a folder, save `social/<piece>/hooks.md` with all candidates, their template and score and, for the top three, the full card:

```markdown
## Reading of the piece
- Payoff, format, platform and length, what is true, angles found, templates of the last three pieces, assumptions

## <Hook> (N/16)
- Template (code and name), spoken line, second line, first frame, on-screen text
- Delivery, where it is paid off, proof before second 10, why this one

## Risks and verification
```

Translate the headings into the user's language. If the piece has no folder yet, the candidates stay in the chat and no folder is created for them; `hooks.md` is saved when the folder is created, by the skill that creates it (`write-short-video-script` does it when it delivers the script).

**Record the choice.** When the user chooses, write the hook in one line with this exact format, which other skills and the next run of this one read:

```
- Hook: <code> <template name>: "<spoken line>"
```

For example, `- Hook: C4 X versus Y: "Same batter, same pan. So why is this one flat?"`. This skill writes the line at the top of `hooks.md` and, when the piece record exists, in the header of `social/<piece>/piece.md`. When the choice is made inside the plan of `write-short-video-script`, that skill writes the line in the "Hook" section of `script.md` and in `hooks.md` when it creates the piece folder. If the record does not exist yet, the skill that creates it later copies the line into its header and puts the code in the `Hook` column of `social/index.md`.

If the user asks to evaluate an existing hook, answer just as briefly in the chat, with a one-line verdict (works, works with adjustments, change it) and the reason, and propose the corrected version as the recommended hook.

If the user asks to test variants, propose two hooks with different templates for the same script and suggest Trial Reels (Instagram shows the Reel first to non-followers) as the test, comparing trial against trial and changing a single variable. Read the result with the metrics listed in "Metrics to evaluate a hook" of `references/evidence.md`. If the retention curve drops in the first 3 to 5 seconds the problem is the hook; if it drops later, the problem is in the script.

## Rules

- The hook is written as the creator would say it out loud. A proven template is fine; if the execution sounds like a generic creator, rewrite it with the concrete detail of the piece.
- Punctuation and style follow the brand's voice guide (`brand-guide/voice-and-humor.md`) when it sets rules for public text.
- Write the line in the creator's own voice, as the voice guide describes it; do not flatten it or force expressions that are not theirs.
- Keep each term in the form the audience says and searches for. A trade term stays out of the first line if part of the audience does not recognize it.
- Separate fact, inference and opinion: a data hook requires a source; a contrarian hook requires the script to support the stance with evidence.
- Do not promise in the hook something the script does not demonstrate. When in doubt, lower the promise, do not raise the script.
- Humor in the hook only if it does not sacrifice clarity at second 3. In sketches, the hook is the premise in action, not a joke beforehand.
- This skill does not publish, schedule or approve anything. The final hook is approved by the user.
