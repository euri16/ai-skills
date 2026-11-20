---
name: capture-lesson
description: 'Turn a correction from the user into a lasting change in the right project document, proposed as an exact diff and written only after the user approves it, so the next session already knows it. Use when the user corrects the agent, redoes or changes its work, repeats an instruction they gave before, or states a preference with "always" or "never" ("no, that is wrong", "I told you last time", "from now on", "remember this", "save this as a rule"). Also use at the end of a task to collect what was learned. Does not create the project map (create-agents-map) or package a whole task as a skill (turn-task-into-skill).'
---

# Capture Lesson

A correction that only lives in the conversation is lost when the session ends, and the user has to repeat it. This skill puts it where the next agent will read it, with the user's approval, so every correction is made once.

Write everything the user reads (the proposal, the question, the confirmation) in the user's language. Write the lesson in the language of the document that receives it.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If an optional item is missing, say once what will be skipped and continue without it. Never invent a document structure the project does not have. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| A root map (`AGENTS.md` or the instruction file the user's agent reads) | No | Knowing where each kind of lesson belongs | Run `create-agents-map`. Without a map, ask the user where the lesson should live |
| Write access to the project's documents | Yes | Writing the approved change | Work inside the project folder |

## Flow

1. **Recognize the lesson.** A lesson is a correction or preference that will matter again: the user says something was wrong, changes your output, repeats an instruction or states a rule. An instruction for this task only ("for now", "this time", "in this file") is not a lesson: apply it and do not store it. When unsure, ask.
2. **Fix the work first.** The correction applies now, before anything is stored.
3. **Write the lesson as a rule.** One general rule in the present tense, plus the reason when it helps to apply it well. No story of how it came up, no dates, no names. Test: would a new session, reading only this, do the right thing?
4. **Find its home.** The most specific document an agent will read when the situation comes back:
   - the skill of the task, if the lesson is about a task a skill covers (`SKILL.md` for the flow, `references/` for detail);
   - the README of the folder where it applies;
   - the root map, only if it applies to the whole project and fits in one line;
   - a script or a check, if the rule is exact and a program can verify it: propose `promote-rule-to-script`.

   Search the project's documents for a rule on the same subject before adding one. If it exists, update it; if the new lesson contradicts it, the new one replaces it.
5. **Propose.** Show in the chat the document path, why it goes there and the exact change as a diff (or before and after), then ask for approval with the agent's structured question tool if it has one. Options: approve, change the wording, use another document, do not store it.
6. **Write after approval.** Integrate the rule into the section it belongs to and reread the whole section so it reads as one text: never paste a "lesson learned" note at the end of a file or inside a step about something else. If the rule changes a value (a limit, a name, a path), update everything that depends on it: other documents, scripts, examples.
7. **Confirm** in one line: the file changed and the rule as it now reads.

## Rules

- Nothing is written without the user's approval of that exact change.
- One lesson, one place. A rule repeated in two documents drifts apart; the second place links to the first.
- Documents describe how things are now. When a rule changes, the old wording is replaced, not kept beside the new one.
- Never store secrets, credentials or personal data in a document.
- If a document grows past what an agent reads comfortably, propose moving its detail to a reference file and leaving a pointer.
