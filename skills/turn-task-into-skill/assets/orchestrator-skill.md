---
name: <verb-object>
description: 'Entry point for <area of work>: decides which skill handles each kind of request, what each stage reads and where the user approves, and keeps the state of work in progress so any session can resume it. Use when <the phrases people use to start or continue this kind of work>.'
---

# <Skill Title>

<What area of work this covers and what a finished result looks like.>

## Resume first

If `<work-folder>/STATUS.md` exists, read it before anything else and continue from its "Next step". If it does not, copy `assets/status.md` there when the work starts.

## Routes

| Kind of work | How to recognize it | Goes to | Reads |
|---|---|---|---|
| <Kind A> | <Phrases or files that identify it> | Skill `<skill-a>` | `<document-a>` |
| <Kind B> | <Phrases or files that identify it> | Skill `<skill-b>` | `<document-b>` |
| Anything else | | Ask the user before starting | |

## Handing out work

- Each stage, or each subagent, receives only the documents its route lists plus the state file. Less context means fewer mistakes.
- One owner per file: two stages never edit the same file at the same time.
- A stage ends by updating the state file: what it did, what was decided and the next step.

## Approval gates

- <The points where the user approves before the work continues, for example: the plan, the final change, anything public or irreversible.>

## Finish

When the work is done, confirm it with the user, record the outcome where the project keeps it and remove the state file or mark it done.
