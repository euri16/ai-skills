---
name: turn-task-into-skill
description: 'Package a task the user repeats as a skill an agent can run the same way every time: gather the real steps, choose between a minimal skill and an orchestrator (a skill with a table of routes that hands each kind of work to the right skill and keeps a state file to resume it), write SKILL.md with its references, scripts and templates, test it on a real case and register it in the project map. Use when the same task has been explained to an agent more than once, when a task has many steps or approvals, or when the user asks to "make a skill", "turn this into a skill", "automate how we do X" or "save this workflow". Does not store a single correction (capture-lesson).'
---

# Turn Task Into Skill

A skill is a folder with a `SKILL.md`: a description that tells the agent when to use it, and the steps, rules and files to do the task well. An agent with skill support reads the description of every skill and opens the full skill only when the task matches, so a project can hold many skills without filling every session with them. With any other agent, the project map points to the `SKILL.md` and the agent reads it as a document when the map sends it there.

Write everything the user reads (questions, drafts, summaries) in the user's language. Write the skill in the language of the project's other skills, or English if there are none.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If an optional item is missing, say once what will be skipped and continue without it. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| The folder where the user's agent loads skills from | Yes | Writing the new skill where it will be found | Ask the user. Common locations are `.agents/skills/` and `.claude/skills/`; one folder linked for several agents keeps a single copy |
| A root map (`AGENTS.md`) | No | Registering the skill in the "Where to go" table | Run `create-agents-map`. Without a map, skip the registration and say so |

## Flow

1. **Pick the task.** The one done most often, or corrected most often. If the user has not named one, propose candidates from the conversation and the project.
2. **Gather the real steps.** From the user, from a conversation where the task was just done, from existing documents and commands. Ask what "done" looks like and which steps need the user's approval. Do not invent steps nobody does.
3. **Choose the shape.**
   - **Minimal skill** (`assets/minimal-skill.md`): one task with one flow.
   - **Orchestrator** (`assets/orchestrator-skill.md`): the work comes in several kinds or stages, each handled by its own skill or document. The orchestrator holds the route table, decides what each stage or subagent reads, sets the approval gates and keeps a state file (`assets/status.md`) so a new session can resume. Build the stage skills first, then the orchestrator that routes to them.
4. **Name it.** Verb plus object, lowercase, words joined by hyphens: `release-version`, `triage-bug`, `write-weekly-report`. The folder name and the `name:` field match.
5. **Write the description.** What it does, when to use it with the phrases the user really says, and which nearby task it does not cover. It decides whether the agent ever opens the skill, so it is specific.
6. **Write the body.**
   - `SKILL.md` stays short: the flow and its rules.
   - Detail an agent needs only in some cases goes to `references/`, linked from the step that needs it.
   - Exact steps that repeat (formatting, validation, a fixed sequence of commands) become `scripts/`; see `promote-rule-to-script`.
   - Templates the task fills go to `assets/`.
   - If the task depends on project files, environment variables, tools or accounts, add a "Prerequisites" section like the one in this skill, so the agent says what is missing before starting.
   - If it needs another skill, name it and invoke it; do not copy its content.
   - Each fact lives in one file.
7. **Approve.** Show the full `SKILL.md` and the list of files in the chat and wait for explicit approval before writing them.
8. **Test it.** Run the skill on a real case reading only the skill, as a new session would. Every question the agent had to ask or every step it got wrong is a gap: fix the skill and repeat.
9. **Register it.** Add a row to the "Where to go" table of the project map pointing to the new skill.

## Rules

- A skill describes how the task is done now. It holds no history of how it came to be.
- Keep project secrets out of skills; they come from environment variables named in Prerequisites.
- Prefer improving an existing skill over creating one that overlaps it.
