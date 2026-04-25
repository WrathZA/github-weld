---
name: gh-weld-init
description: Scaffold a new project's README.md and CLAUDE.md via a guided abstract interview, then wire in gh-weld. Use when starting a new repo or when a project lacks CLAUDE.md or README. Trigger phrases: "init this project", "scaffold", "set up this repo", "create README", "new project setup", "initialize", "CLAUDE.md conventions".
compatibility: Requires git and gh CLI. Designed for Claude Code with gh-weld installed.
---

# gh-weld-init

## NEVER

- **NEVER ask about technology, language, stack, or frameworks**
  **Instead:** Ask only abstract questions — goals, audience, tone, scope, seriousness.
  **Why:** Tech details produce CLAUDE.md boilerplate the user must clean up; abstract framing produces durable conventions that outlast stack changes.

- **NEVER write files before the user accepts the final recap**
  **Instead:** Complete the full interview and get (a)ccept at the Phase 3 gate first.
  **Why:** Writing early locks in unreviewed answers and overwrites existing files without consent.

- **NEVER write file content with shell commands**
  **Instead:** Use the Write tool for README.md, CLAUDE.md, and any temp files.
  **Why:** Heredocs with `#`-prefixed lines trigger Claude Code's security check on every execution.

- **NEVER run `gh-weld-install` before both files are written**
  **Instead:** Write README.md then CLAUDE.md, then invoke the install skill.
  **Why:** `gh-weld-install` appends to CLAUDE.md — running it before generation corrupts the result.

- **NEVER generate generic boilerplate sections**
  **Instead:** Write only sections directly implied by the interview recap.
  **Why:** A README with five generic headings and placeholder text is worse than a short honest one.

- **NEVER use the Write tool on an existing `.gitignore`**
  **Instead:** Read it first, check for the entry, then append only if missing.
  **Why:** Write overwrites the entire file, silently destroying existing ignore rules.

---

## Phase 1 — Idempotency Check

First, verify the current directory is a git repo:

```bash
git rev-parse --is-inside-work-tree
```

If the command fails or returns anything other than `true`: run `git init` as a separate Bash call to initialize a new repository, then continue.

Use Glob to check for existing files:

- Glob `README.md` in the current directory
- Glob `CLAUDE.md` in the current directory

**If both exist:** Read both files. Show a recap of what they currently say — purpose, audience, tone, scope. Then ask (single keypress):

```
README.md and CLAUDE.md already exist.
(a)ccept current state / (u)pdate with fresh interview / (r)efine existing content
```

- **(a)**: Stop — nothing to do.
- **(u)**: Proceed to Phase 2 (full interview from scratch; both files will be overwritten on accept).
- **(r)**: Proceed to Phase 2 but pre-fill the recap from existing content; user amends rather than restarts.

**If one file exists:** Warn which file exists. Ask `<filename> already exists — overwrite it? (y/n)`. If no: skip generating that file only; continue with the other.

**If neither exists:** Proceed directly to Phase 2.

---

## Phase 2 — Interview

Generate abstract questions one at a time. Let the project context (directory name, any existing files, prior answers) inform which questions to ask — do not follow a fixed list. Good question domains: project purpose and goals, intended audience, scope and explicit out-of-scope boundaries, tone (serious vs. playful, strict vs. forgiving), and whether this is a hobby or professional project.

**All answers are long-form free text.** Do not offer multiple-choice options during the interview.

After each answer, display an updated recap:

```
## Project Recap

**Purpose:** [what you've learned, or "unknown"]
**Audience:** [what you've learned, or "unknown"]
**Scope:** [what you've learned, or "unknown"]
**Tone:** [what you've learned, or "unknown"]
**Type:** [hobby / professional / unknown]
```

Continue until the recap has no "unknown" in Purpose, Audience, or Tone — those three are required before moving to Phase 3. Scope and Type may be inferred if the user hasn't addressed them. Typically 4–6 questions suffice; stop when you have enough to write with genuine framing.

---

## Phase 3 — Recap Gate

Show the complete final recap. Ask (single keypress):

```
(a)ccept and generate files / (r)evise
```

- **(a)**: Proceed to Phase 4.
- **(r)**: Ask "What would you like to change?" Collect the answer, update the recap, and loop back to this gate.

Do not proceed to Phase 4 until the user explicitly accepts.

---

## Phase 4 — Generate Files

**README.md** — write via Write tool.

Shape every decision from the recap: framing, tone, what's included and omitted. Consider these sections (not all required — include only what the recap warrants): project name and one-line purpose, who it's for, what it does and doesn't do, a tone-appropriate closing. A three-section README that matches the project's character is better than eight generic sections.

**CLAUDE.md** — write via Write tool.

Derive all conventions from the recap. Translate recap answers into voice and constraint level using these pairs:

- **serious / professional** → imperative voice, explicit constraints, no hedging ("always", "never", "must")
- **playful / hobby** → casual voice, encouragement over rules ("try to", "prefer", "feel free to")
- **narrow scope** → include explicit out-of-scope statements the agent should respect
- **broad / exploratory scope** → emphasize judgment over rules; fewer hard constraints

Include: 1–2 sentences of project purpose, coding philosophy derived from tone and seriousness, and any scope boundaries the agent should respect. Do not include technology-specific guidance — that's out of scope for this skill.

**`.gitignore`** — after writing both files, ensure `settings.local.json` is excluded from git. This file contains user-local Claude Code config (path overrides, local permissions) that is machine-specific and must not be committed to shared repos.

Use Glob to check if `.gitignore` exists in the current directory. If it does not exist, create it via the Write tool with `settings.local.json` as the first entry. If it exists, read it and append `settings.local.json` on a new line only if it is not already present.

---

## Phase 5 — Wire gh-weld

Invoke `/gh-weld-install` to wire gh-weld into the repo. If `gh-weld-install` is not installed, skip it and tell the user: "Install gh-weld and run `/gh-weld-install` manually to complete the setup."

Output when done:

```
README.md and CLAUDE.md written. gh-weld is wired in.

Next: /gh-weld-issue to file your first issue, or /gh-weld-next to pick one up.
```
