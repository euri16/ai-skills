---
name: research-content-topic
description: Frame one content idea quickly for a creator's brand, check the few claims the piece will state, find a differentiated thesis and recommend the best angle, channel and depth. Use before an article, video or post when the question is what to say about a topic and whether its claims hold ("research this topic", "what angle should I take", "check this before the post"). Do not use to write the final piece.
---

# Research Content Topic

Write everything the user reads (chat, questions, the recommendation) in the user's language, or in the one the workspace instructions set.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| Web search and page reading in the agent | Yes | Finding primary sources and reading each one before citing it | Enable the agent's web search and fetch tools (in Claude Code, `WebSearch` and `WebFetch`, allowed in the permission settings) |
| `brand-guide/positioning.md`, `brand-guide/audiences.md`, `editorial/pillars.md` | No | A thesis and an angle that fit what the creator promises, who the content is for and which pillar it serves | Write them following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/` there has filled-in examples at the same paths |
| `editorial/<channel>.md` | No | Format and depth for the channel, when the user already chose one | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/editorial/` there has a filled-in channel guide (`instagram.md`) |
| `operations/research-policy.md` | No | What must be verified, and how, before a claim goes into public content | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/operations/research-policy.md` there is a filled-in example |

## Load context

Read the workspace files of the table that exist, for what each one is used for.

## Turn the idea into a useful question

1. Define what the audience should understand, decide or build.
2. Identify the real tension: problem, disagreement, limitation or change.
3. Separate the editorial question from a generic information search.
4. Flag which part the creator can support with documented experience and which needs external sources.

## Research

1. Create a short map of questions.
2. Look for primary evidence, in its current form: a source that has been revised or replaced does not count.
3. Try the method, the product or the example yourself when that is reasonable.
4. Look for counterarguments and for the conditions under which the claim stops holding.
5. Record each claim with its source, the date of the source or of the day it was checked, its confidence (scale below) and the condition under which it holds.
6. Do not invent a personal experience to fill a narrative gap.
7. Stop researching when there is enough evidence to choose thesis, conditions and format. Do not expand into adjacent topics that cannot change the recommended piece.

Confidence scale:

- **High:** a primary source read directly states it for the date and place in question, or two independent reputable sources agree.
- **Medium:** one reputable secondary source states it, or a primary source that is dated, partial or covers a narrower case.
- **Low:** a single unverified source, a vendor's claim about its own product, an anecdote or the agent's own inference. A low-confidence claim is never stated as fact in public content.

## Recommend the content

Save the recommendation as a Markdown file and answer in the chat with its path, the thesis and the recommended angle. If the research serves one piece that already has a folder, save it as `research.md` in that folder (`social/<piece>/research.md`); otherwise save it in the workspace's `reports/` folder as `reports/YYYY-MM-DD-<slug>.md`, with the date the research was done. The file contains:

```markdown
## Editorial recommendation
- Main thesis
- Why it matters now
- Audience and transformation
- Recommended channel and format

## Evidence and claims
| Claim | Source | Date | Confidence | Condition |
|---|---|---|---|---|

## Main angle
- Possible hook
- Line of argument
- Demonstration or example
- Limit that must be included

## Alternative angles
## Risks and gaps
## Sources
```

Translate the headings into the user's language.

Recommend a single direction by default. Fill "Alternative angles" only with angles that would change the audience, the thesis or the production; otherwise leave the section out.
