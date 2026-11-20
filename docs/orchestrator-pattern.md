# The orchestrator pattern

[Leer en español](orchestrator-pattern.es.md)

An agent forgets everything between sessions. What it knows about your project is what it reads when the session starts. This pattern puts the project's knowledge on disk: how work is done (process) and what the project is about (domain), in small documents the agent opens only when the task needs them. Two rules keep those documents true, and the rules that are exact become scripts.

It does not depend on any particular agent. Everything is plain Markdown files and scripts in your repository.

## The pieces

| Piece | What it holds | When the agent reads it |
|---|---|---|
| `AGENTS.md` at the root | The map: what the project is, how work is done, where to go for each kind of task, what never happens, and the two rules | At the start of every session |
| A README per folder | What lives in the folder and how to work there | When the task touches that folder |
| Skills | How to do a repeated task, step by step, with its scripts and templates | When the task matches the skill's description |
| An orchestrator | A skill with a table of routes: which skill handles each kind of work, what each stage reads, where the user approves | When the work has several kinds or stages |
| State files | Where unfinished work stands and what the next step is | When a new session resumes the work |
| Scripts | The rules a program can check or apply | Nobody has to remember them: they run |

```
AGENTS.md (the map)
  -> <folder>/README.md            how to work in that folder
  -> skills/<task>/SKILL.md        how to do one repeated task
       -> scripts/                 the exact steps
  -> skills/<orchestrator>/        routes work to the task skills
       -> STATUS.md                where the work stands
```

The orchestrator decides what each agent reads. A stage, or a subagent, gets only the documents its route lists plus the state file: less context, fewer mistakes, and any session can pick the work up where the last one left it.

## The two rules

These two lines go in the map. They are what makes the system improve on its own instead of decaying.

1. **When I correct you, propose which document should keep the lesson, show me the exact change and wait for my approval before writing it.**
   Every correction is made once. The next session already knows it. Approval keeps you in charge of what becomes a rule, and seeing the exact change keeps the documents short.
2. **When a document and the code disagree, the code wins: work from the code and propose the fix to the document.**
   The code is what runs. An outdated document is fixed, never followed.

## How to start

1. **Write the map.** Around 20 lines: what the project is, how work is done, where to go for each task, what never happens. `create-agents-map` interviews you and writes it from [the template](../skills/create-agents-map/assets/AGENTS.md).
2. **Add the two rules.** They are already in the template. `capture-lesson` applies the first one every time you correct the agent; `review-stale-docs` applies the second one across the project.
3. **A README per folder** the map points to: what lives there and how to work there. [Template](../skills/create-agents-map/assets/folder-README.md).
4. **A skill for your most frequent task.** `turn-task-into-skill` packages it as a [minimal skill](../skills/turn-task-into-skill/assets/minimal-skill.md), or as an [orchestrator](../skills/turn-task-into-skill/assets/orchestrator-skill.md) with a [state file](../skills/turn-task-into-skill/assets/status.md) when the work has several stages.
5. **Move what is exact to a script.** `promote-rule-to-script` finds the rules a program can check and proposes the script or the hook. [`check-docs.py`](../skills/review-stale-docs/scripts/check-docs.py) is an example: it checks that the links and paths in your documents still exist.

## The skills

| Skill | What it does |
|---|---|
| [`create-agents-map`](../skills/create-agents-map) | Interviews you and writes the root `AGENTS.md` with the two rules; optionally a README per folder |
| [`capture-lesson`](../skills/capture-lesson) | Turns a correction into an exact change in the right document, written after your approval |
| [`turn-task-into-skill`](../skills/turn-task-into-skill) | Packages a repeated task as a minimal skill or an orchestrator with a state file |
| [`promote-rule-to-script`](../skills/promote-rule-to-script) | Finds exact, repeated rules and proposes a script or a hook for each |
| [`review-stale-docs`](../skills/review-stale-docs) | Compares documents and skills with the code, applies "the code wins" and proposes fixes and retirements |

Skills that need something from your project (a map, a tool) start with a "Prerequisites" check and tell you what is missing before doing anything.

## Templates

| Template | Use |
|---|---|
| [`AGENTS.md`](../skills/create-agents-map/assets/AGENTS.md) | The root map, with the two rules |
| [`folder-README.md`](../skills/create-agents-map/assets/folder-README.md) | The README of a folder |
| [`minimal-skill.md`](../skills/turn-task-into-skill/assets/minimal-skill.md) | A skill with one flow; save it as `<skill-name>/SKILL.md` |
| [`orchestrator-skill.md`](../skills/turn-task-into-skill/assets/orchestrator-skill.md) | A skill with a table of routes; save it as `<skill-name>/SKILL.md` |
| [`status.md`](../skills/turn-task-into-skill/assets/status.md) | The state file of work in progress |

The templates live inside the skills that use them, so each skill works when it is installed on its own.

## With any agent

- Several agents read `AGENTS.md` at the root of the repository. For one that reads a different file name, create that file with a single line that points to `AGENTS.md`, so the rules live in one place.
- A skill is a folder with a `SKILL.md` file. Agents that support skills load them from their skills folder (for example `.agents/skills/` or `.claude/skills/`). With an agent that does not, the map can still point to a `SKILL.md` as a document to read before the task.

## What to avoid

- **One giant instructions file.** The agent reads all of it every time and follows less of it. Keep the map short and the detail next to what it describes.
- **Storing every instruction.** "For now" and "in this file" are not rules. Only what will matter again is stored.
- **Writing lessons without approval.** The documents drift toward what the agent guessed instead of what you decided.
- **History in the documents.** Documents say how things are now. When a rule changes, the old wording is replaced.
- **The same rule in two places.** One copy goes stale. Keep it in one place and link to it.
