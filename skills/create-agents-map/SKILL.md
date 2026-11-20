---
name: create-agents-map
description: 'Interview the user and create the root AGENTS.md of a project: a short map of what the project is, how work is done in it, where to go for each kind of task and what is never done, plus the two rules that keep the documents alive (every correction is stored with approval; when a document and the code disagree, the code wins). Optionally adds a README to the folders the map points to. Use when starting to work with coding agents on a project, when a project has no AGENTS.md or has one that grew into a wall of text, or when the user says they keep repeating the same instructions to the agent ("create an AGENTS.md", "set up this repo for agents", "I am tired of explaining this every session"). Does not write skills (turn-task-into-skill) or store a single correction (capture-lesson).'
---

# Create Agents Map

An agent starts every session knowing nothing about the project. What it knows is what it reads, so the root `AGENTS.md` is a map: a page that says what the project is, how work is done and where the detail lives. It is not a manual. The detail lives next to what it describes (a README per folder, a skill per repeated task), and the map points to it so the agent reads only what the task needs.

Write everything the user reads (questions, drafts, summaries) in the user's language. Write the map in the language the project's documents already use, or the one the user picks.

## Inspect before asking

Read what already exists so the interview only asks what the files cannot answer:

- An existing `AGENTS.md`, or any other instruction file an agent reads (for example `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`), and the root `README.md`.
- The folder tree, two levels deep, without dependency or build folders.
- Manifests and task runners (`package.json`, `pyproject.toml`, `Makefile`, `build.gradle`, `Cargo.toml` and similar), CI files and `scripts/`: the real build, test and run commands come from here.
- Existing skills folders (`.agents/skills/`, `.claude/skills/`, `skills/`) and `docs/`.

Use these files to pre-fill answers, never to invent them. A command goes in the map only if it exists in a manifest or a script, or the user gives it.

## Interview

Ask with the agent's structured question tool if it has one, grouping the independent questions in one call and offering the answers you inferred as options:

1. What is the project, in one sentence, and who is it for?
2. What do you repeat most often to an agent working here? Ask for three to five things.
3. How is work done: build, test and run commands, branches and commits, what must pass before something is done?
4. Where does each kind of task go: which folder, document or skill holds the detail for each one?
5. What must never happen without your approval (pushing, deploying, publishing, deleting, spending money, touching production data)?
6. Where does unfinished work leave its state so a new session can resume it?

Stop at what is needed for a first map. A map that grows from real corrections (`capture-lesson`) beats a long one written on day one.

## Write the map

Start from `assets/AGENTS.md` and keep it near 20 lines, never above 40.

- **Pointers, not content.** A line that explains how a folder works belongs in that folder's README; the map links to it.
- **Each line earns its place.** Keep a line only if an agent would do something wrong without it. Delete the generic advice any agent already follows ("write clean code").
- **Concrete over abstract.** Real commands, real paths, real names of skills.
- **The two rules are mandatory**, worded as in the template and adapted only in language:
  1. When I correct you, propose which document should keep the lesson, show me the exact change and wait for my approval before writing it.
  2. When a document and the code disagree, the code wins: work from the code and propose the fix to the document.

Show the full map in the chat and wait for explicit approval before writing it. If an `AGENTS.md` already exists, show the change as a diff and keep every line the user did not ask to drop.

## Make every agent read it

Several agents read `AGENTS.md` at the root. Ask which agents the user works with; for one that reads a different file name, create that file with a single line that points to `AGENTS.md` (or imports it, if that tool has an import syntax), so the rules live in one file.

## Folder READMEs (optional)

For each folder the map routes to that has no README, offer one from `assets/folder-README.md`: what lives there, how to work there, related skills. Write them one at a time, each shown and approved. A folder whose content explains itself does not need one.

## Close

Report the files written and suggest the next steps: `capture-lesson` the next time the user corrects the agent, and `turn-task-into-skill` for the task the user repeats most.
