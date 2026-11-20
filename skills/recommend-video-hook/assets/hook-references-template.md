# Hook references

Hooks from creators the user likes, analyzed to copy their structure, never their content: transcribe the first line of a video that performed well, keep the structure and fill it with the facts of the new piece. `recommend-video-hook` reads this file before proposing and prioritizes it over its general templates, because it reflects the brand's taste.

This file lives in the workspace as `editorial/hook-references.md`.

## Videos and accounts

When the user shares a video or an account as a reference, invoke the `analyze-video` skill through the skill tool to transcribe the first seconds and extract the frames from 0 to 3 s, and add a row. Without that skill, ask the user for the first line and describe frame 0 from what they say. The "Template" column carries the code and name of the closest template in the skill's `references/hook-templates.md`.

| Date | Creator and link | First line | Frame 0 | On-screen text | Template | What is taken |
|---|---|---|---|---|---|---|

## Articles and guides

When the user shares an article or a guide about hooks, read it and add a row with what it contributes: a spoken formula, a visual device or a piece of evidence, with the template it belongs to.

| Date | Source and link | What it says | Template | How it is used |
|---|---|---|---|---|
