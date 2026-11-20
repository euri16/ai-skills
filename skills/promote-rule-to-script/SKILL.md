---
name: promote-rule-to-script
description: 'Find the rules in a project''s documents and skills that are exact and repeated (a format, a naming pattern, a limit, a required field, a fixed sequence of commands, a check before finishing) and propose turning each one into a script or a hook, so it runs the same way every time instead of depending on the agent remembering it. Use when the same mistake was corrected twice, when a rule says "always" or "never" about something a program could check, when documents grow with mechanical rules, or when the user asks to "automate this rule", "make a check for this", "add a hook" or "stop the agent from forgetting X". Does not decide matters of judgment such as tone, design or priorities.'
---

# Promote Rule To Script

Agents follow written rules most of the time, which is not every time. A rule that a program can decide (pass or fail, right or wrong format, present or missing) is safer as a script: it gives the same answer every run, costs nothing to read and fails loudly. The document keeps one line that says to run it.

Write everything the user reads (the candidate list, questions, summaries) in the user's language. Scripts, their messages and comments follow the language of the project's code.

## Prerequisites

Check these when the skill is invoked, before doing anything else. If a required item is missing, stop and tell the user what is missing, what it is needed for and how to set it up. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| Project documents with rules: a root map (`AGENTS.md`), folder READMEs or skills | Yes | Finding the candidate rules | Run `create-agents-map`, or point the skill at the documents that hold the rules |
| A runtime the project already uses for scripts (shell, Python, Node or similar) | Yes | Running the new scripts | Use what the project's existing scripts use; ask before adding a new runtime |

## Flow

1. **Find candidates.** Read the map, the folder READMEs and the skills looking for rules with "always", "never" or "must" about something checkable: a pattern, a count, a path, a field, a date, an order of commands. Add the corrections that repeat: a mistake fixed twice is a candidate even if no document states it yet.
2. **Separate exact from judgment.** Exact: a program can decide it without opinion. Judgment: tone, clarity, design, priorities. Only exact rules are promoted; judgment stays in the documents.
3. **Choose the form** for each exact rule:
   - **Check:** validates and exits with an error and a clear message. The default.
   - **Fixer:** applies the change itself, when the right result is unambiguous (formatting, sorting, generated files).
   - **Hook:** runs a check or a fixer automatically on an event (before a commit, in CI, after the agent edits a file), when forgetting it is costly. Use the hook mechanism the project already has; ask before adding a new one.
   - **Wrapper:** one command for a fixed sequence that people or agents run by hand step by step.
4. **Propose a table:** the rule, where it is written, the form, the trigger, and the line the document keeps after the change (for example "Run `scripts/check-names.sh` before committing"). Show it in the chat and ask which ones to build.
5. **Build each approved one,** one at a time:
   - Small and readable, with no dependencies beyond what the project has.
   - A `--help`, an error message that says what is wrong and how to fix it, and exit code 0 when it passes and non-zero when it fails.
   - Test it against a case that passes and a case that fails, and show both outputs.
   - Wire it into a hook or CI only with the user's approval.
6. **Update the document.** Replace the rule's long explanation with the line that runs the script, so the rule is in one place: the script.

## Example

`scripts/check-docs.py` of the `review-stale-docs` skill, when that skill is installed next to this one, is a check of this kind. It verifies that the links and paths written in the project's documents point to files that exist and that review dates are recent, and exits non-zero otherwise. Run before a commit or in CI, it turns the rule "keep the documents in sync with the code" into something a program enforces.

## Rules

- A script never replaces the user's approval for anything public or irreversible; it can only check before asking.
- Do not promote a rule the user has not confirmed is still valid; check it against the code first.
- Prefer one clear check per rule over one large script that checks everything.
