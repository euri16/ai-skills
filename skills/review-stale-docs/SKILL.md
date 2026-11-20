---
name: review-stale-docs
description: 'Review a project''s documents and skills against its code: find links and paths that no longer exist, commands, settings and names the code no longer has, rules that contradict what the code does, and documents or skills nobody uses; apply the rule that the code wins over the documents, and propose each fix or retirement for the user to approve. Use periodically, after a large refactor or migration, when an agent followed an outdated instruction, or when the user asks to "review the docs", "find stale documentation", "clean up the skills" or "check the docs against the code". Does not change the code to match a document.'
---

# Review Stale Docs

An outdated document is worse than none: the agent trusts it and does the wrong thing with confidence. This review compares what the documents say with what the code does and resolves every difference with one rule: the code wins, and the document is fixed. What nobody uses is retired, so what remains is short and true.

Write everything the user reads (the report, questions, summaries) in the user's language.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user what is missing, what it is needed for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| Python 3.7 or later (`python3`) | No | Running `scripts/check-docs.py`, the mechanical part of the review | Install it from python.org or the system package manager. Without it, do step 2 by reading the documents |
| Version control history (`git`) | No | Seeing when the code and a document last changed | Without it, skip the dates and compare the content only |

## Flow

1. **Scope.** By default: the root map (`AGENTS.md` and any instruction file that points to it), every README, `docs/` and the skills folder. The user can narrow it to a folder.
2. **Mechanical check.** Run `python3 scripts/check-docs.py <project-root>` (`--help` lists the options). It reports broken links, paths in backticks that do not exist, review dates older than the limit when documents carry a `Last reviewed: YYYY-MM-DD` line, and documents no other document links to or names.
3. **Compare content with code.** For each document in scope, check what a script cannot:
   - Commands against the manifests, task runners and scripts that define them.
   - Settings and environment variables against the code that reads them.
   - Folder structure, file names and module names against the tree.
   - Versions, limits and default values against the code and configuration.
   - Rules against what the code really does.
   - Skills: does the flow still match the tools and files it names? Was it used recently (ask the user if there is no way to tell)?
   Note each difference with its evidence: the document line and the code `file:line`.
4. **Classify each finding.**
   - **The document is wrong:** the code wins. Propose the fix to the document.
   - **The document describes something removed:** propose deleting that section, or the document if nothing remains.
   - **The code looks wrong against what the document intends:** do not change either. Ask the user; if the code is the bug, it is a code fix for another task, not a documentation fix.
   - **Unused:** a document no other document points to, or a skill no one invokes. Propose retiring it: deleting it through version control, or moving it to an archive folder outside what agents read.
   - **Duplicated:** the same rule in two places. Propose keeping one and linking to it from the other.
5. **Report.** A table in the chat: file, finding, evidence, proposed change. Group the findings by type and ask for approval per group with the agent's structured question tool if it has one; the user can exclude any row.
6. **Apply the approved changes,** run `scripts/check-docs.py` again and show that the approved findings are gone. If the project uses review dates, update `Last reviewed:` in every document that was reviewed.

## Rules

- Nothing is deleted, moved or rewritten without the user's approval of that finding.
- Never change code to make it match a document.
- A fix replaces the outdated text; it does not add a note saying what changed.
