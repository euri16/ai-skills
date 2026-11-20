---
name: write-caption
description: 'Write the caption of a social piece (Instagram Reel, carousel or post) and its version for TikTok, YouTube Shorts (title and description) and LinkedIn video, with rules based on what the platforms and the data say works: a first line that hooks and carries the words someone would search for, no summarizing the video, a single real CTA and at most 5 hashtags (0 to 3 on LinkedIn). Use whenever the user asks for a caption, a description, copy or the text to publish a piece from `social/`, to improve one, shorten it or adapt it to another network, even if they do not say "caption". Does not write the text of carousel slides or LinkedIn posts without video.'
---

# Write Caption

The caption does not make a video go viral: on every platform the feed moves on what the viewer does (watch time, sends, likes). The caption has three jobs: that the first line gives a reason to stay, save or send; that the platforms know what the piece is about, because their search engines (and Google, on Instagram) read the text; and to not get in the way. Before "more" only one or two lines are visible, so that line is the caption. The rest is optional and almost always unnecessary.

Write the captions in the language of the piece, and everything the user reads (chat, questions) in the user's language or in the one the workspace instructions set.

The writing rules below are defaults; the brand guide and the workspace instructions win when they say otherwise. The platform limits (hashtags, characters) are not defaults: they come from `references/platforms.md`.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| The piece's content in `social/<piece>/`: the transcript of the final video (`edit/analysis/final-video/`) or its export (`export/`), otherwise `script.md`; for a carousel or post, the piece's slides, wherever the workspace keeps them | Yes | Writing from what the piece really says | Produced by the earlier stages (`write-short-video-script`, the edit, `analyze-video`) with the folder layout of `CONVENTIONS.md` in the ai-skills repo; or share the video or its text in the chat |
| `social/<piece>/piece.md` | No | The cover headline, the spoken hook (its `- Hook:` line) and the music license to respect, and the place where the approved captions are saved | If it does not exist, create it at approval (step 9) with the header and fields `CONVENTIONS.md` in the ai-skills repo describes |
| `brand-guide/voice-and-humor.md`, `brand-guide/writing-style-playbook.md` | No | Writing the caption in the creator's voice and with their writing rules | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/voice-and-humor.md` there is a filled-in example |
| Web search and page reading in the agent | No | Checking a platform limit again when the verification date of `references/platforms.md` is more than six months old; without them, state the limits with that date | Enable the agent's web search and fetch tools |
| `analyze-video` skill | No | Transcribing the export when the final video has no transcript; without it, the caption is written from the script and the user is told it may differ from the video | Install the `analyze-video` skill from the ai-skills repo |

## Load context

- `references/platforms.md`: what each network shows, reads and penalizes, with sources and verification date.
- The creator's voice and writing guides, when the workspace has them.
- The piece: the transcript of the final video (if it does not exist, invoke the `analyze-video` skill on the export), the script and the record. Write from what the video really says, not from the script, because it changes during recording.
- The cover headline and the spoken hook, so as not to repeat them word for word.

## Flow

1. **Understand the piece.** In one sentence: what it is about, what the hook promises, what the punchline is that is not revealed and what the video does not say (a source, a link, a nuance).
2. **Search words.** One to three terms someone would type to find this topic ("sourdough starter", "why is my bread dense", "no-knead bread"). Keep each term in the form the audience searches for: the everyday word or the trade term, in the language and spelling they type it.
3. **First line.** The hook: a sentence that provokes, names the tension or gives the data point, and that contains at least one search word said naturally. It fits in the one or two lines shown before "more": as a working target, one sentence of at most about 125 characters (a figure reported by blogs, not published by any platform; see `references/platforms.md`), checked in a screenshot on the phone when precision matters. It can be a provocation the video turns around, as long as the video answers it; it never promises something the video does not deliver.
4. **Body, only if it adds something.** At most one or two lines with what the video does not say (context, source, the link to what is mentioned). Never a summary or a transcript of the video: if removing the body takes nothing away from someone who already watched the video, it is removed.
5. **One real CTA.** A question the creator wants to read and answer, or save or send when the piece is really useful. Never "comment X to get it", nor asking for likes or followers.
6. **Hashtags.** At most 5 in total, at the end of the caption, specific to the topic and never generic or unrelated. If the piece belongs to a series, the series tag is one of the 5. LinkedIn has its own limit: 0 to 3.
7. **Versions per channel**, with the rules in `references/platforms.md`:
   - **Instagram** (Reel, carousel or post): the base caption. In a carousel, the slide text already tells the idea; the caption still stays short.
   - **TikTok:** the same caption, checking that the search words are in the first line.
   - **YouTube Shorts:** a **title** of up to 100 characters with the search word (it is what is seen and what weighs in search) and the caption as the description.
   - **LinkedIn (video):** a text that describes what the video shows, with a genuine question at the end and no "comment X".
8. **Review.** Spelling and punctuation of the caption's language, with the punctuation rules of the brand's voice guide; no invisible character or exotic space (run the workspace's public-text checker if it has one); every data point verified in the piece's research; nothing invented (experiences, figures, quotes); the first line is understood on its own; hashtags within the limit of step 6.
9. **Approve and save.** Paste in the chat the full, exact text of each version before asking for approval with the agent's structured question tool (`AskUserQuestion` in Claude Code); if they are long texts or many versions, write them in the chat and ask there. With the approval, save it in each channel's section of the piece record `piece.md` (`Caption:` in a code block; on YouTube, also `- Title:`) with its status. If this skill creates the record, it copies the `- Hook:` line into its header from the piece's `hooks.md` or the "Hook" section of `script.md`, and adds the piece's row to `social/index.md` with the hook's template code in the `Hook` column. If the music license is CC BY, the credit goes at the end, after the hashtags: "Music: <title> by <author> (CC BY 4.0)", in the caption's language.

One main version per channel. Propose alternatives only when they really change the hook, and show them in full.

## Rules

- The caption is written in the creator's own voice, as the voice guide describes it, with humor when it comes out naturally.
- No long caption unrelated to the content.
- Emojis reinforce a line that already works without them; they do not replace words.
- Mentions (@) only of accounts that appear in or collaborate on the piece.
- This skill does not publish or schedule anything: scheduling belongs to `schedule-social-piece`, with explicit approval.
