---
name: gh-weld-setup
description: Set up a new or existing project end-to-end: scaffold README.md and CLAUDE.md via a guided abstract interview, wire in gh-weld conventions, and optionally create a GitHub repo. Use when starting a new repo or onboarding an existing project to gh-weld.
when_to_use: "set up this project", "init this repo", "scaffold", "new project setup", "install gh-weld", "wire up weld", "initialize", "create README", "CLAUDE.md conventions", "new repository".
compatibility: Requires git and gh CLI. Claude Code with WebFetch.
---

# gh-weld-setup

End-to-end project setup: scaffold files, wire conventions, create GitHub repo.

## NEVER

- **NEVER ask about technology, language, stack, or frameworks**
  **Instead:** Ask only abstract questions — goals, audience, tone, scope, seriousness.
  **Why:** Tech details produce CLAUDE.md boilerplate the user must clean up; abstract framing produces durable conventions that outlast stack changes.

- **NEVER write files before the user accepts the final recap**
  **Instead:** Complete the full interview and get (a)ccept at the Phase 3 gate first.
  **Why:** Writing early locks in unreviewed answers and may overwrite existing files without consent.

- **NEVER use the Write tool on an existing `.gitignore` without reading it first**
  **Instead:** Read it, check for each entry, then append only missing lines.
  **Why:** Write overwrites the entire file, silently destroying existing ignore rules.

- **NEVER wire conventions.md before both README.md and CLAUDE.md are written**
  **Instead:** Write both files first, then fetch and wire conventions.md.
  **Why:** conventions.md prepends to CLAUDE.md — running it before generation corrupts the result.

- **NEVER append to `.gitignore` or `CLAUDE.md` without checking for the exact line first**
  **Instead:** Search for `.weld/tmp/` and `@.weld/conventions.md` before appending; skip if already present.
  **Why:** Duplicate entries signal the skill isn't idempotent and create noisy diffs.

- **NEVER overwrite `.weld/conventions.md` without showing what changed**
  **Instead:** Compare fetched content to local; if different, note line-count delta before writing.
  **Why:** The user may have local edits; silent overwrite destroys them.

- **NEVER generate generic boilerplate sections**
  **Instead:** Write only sections directly implied by the interview recap.
  **Why:** A README with five generic headings and placeholder text is worse than a short honest one.

- **NEVER chain Bash calls with `&&` or `;`**
  **Instead:** One command per Bash tool call.
  **Why:** Claude Code's safety check fires on multi-command calls and interrupts mid-flow.

- **NEVER use `|` (pipe) in Bash tool calls**
  **Instead:** Redirect output to `.weld/tmp/<file>` with `>` and read back with the Read tool.
  **Why:** Claude Code stops execution on pipe — no error, no warning.
  Note: `|` in markdown table syntax is unaffected.

- **NEVER use `$()` command substitution**
  **Instead:** Write content to a fixed path under `.weld/tmp/` with the Write tool.
  **Why:** Claude Code's permission system prompts on `$()` during execution.

- **NEVER use bash heredoc (`cat > file << 'EOF'`) for content with `#`-prefixed lines**
  **Instead:** Use the Write tool for all file content.
  **Why:** `#`-prefixed lines (headings) trigger Claude Code's security check on every execution.

- **NEVER use `echo >` or `cat` to write file content**
  **Instead:** Use the Write tool.
  **Why:** echo-redirect and cat approaches fail silently on `#`-prefixed content due to Claude Code's security checks.

- **NEVER use `find`, `grep`, or `cat` as Bash commands**
  **Instead:** Use Glob to find files, Grep to search content, and Read to read files.
  **Why:** Built-in tools have tighter permissions and avoid Claude Code safety prompts that raw shell commands trigger.
  Note: this restriction applies only to Bash tool calls — using these words in prose, code examples, or explanations is unaffected.

- **NEVER pass multiline content containing `#`-prefixed lines as an inline `gh` argument**
  **Instead:** Write to `.weld/tmp/<name>.md` with the Write tool and pass via `--body-file`.
  **Why:** Headers in inline `gh` strings trigger an un-suppressible Claude Code permission prompt on every execution.

- **NEVER use the `-i` flag in git commands**
  **Instead:** Use non-interactive equivalents (e.g. `git rebase --onto` instead of `git rebase -i`).
  **Why:** Claude Code runs in a non-interactive shell — `-i` hangs waiting for input that never comes.

- **NEVER skip git hooks with `--no-verify`** unless the user explicitly requests it.
  **Instead:** Investigate and fix the hook failure before committing.
  **Why:** Hooks exist to catch real problems; bypassing them silently hides errors that break CI or deployments.

---

## Phase 1 — Idempotency Check

Verify the current directory is a git repo:

```bash
git rev-parse --is-inside-work-tree
```

If it fails or returns anything other than `true`: run `git init` as a separate Bash call, then continue.

If the repo check passed (not freshly initialised): run `git rev-parse --show-toplevel` as a separate Bash call and write the result to `.weld/tmp/toplevel.txt`. Read it back. If the path does not match the current working directory, ask (single keypress):

```
You're inside a git repo subdirectory, not the root.
Running setup here will scaffold files in this subdirectory.
(c)ontinue here / (Q)uit
```

If (Q): stop. If (c): proceed. Then run `rm .weld/tmp/toplevel.txt`.

Use Glob to check for existing files:
- Glob `README.md` in the current directory
- Glob `CLAUDE.md` in the current directory

**If both exist:** Read both files. Show a recap of what they currently say — purpose, audience, tone, scope. Then ask (single keypress):

```
README.md and CLAUDE.md already exist.
(a)ccept current state / (u)pdate with fresh interview / (r)efine existing content
```

- **(a)**: Skip Phases 2–4 (interview, recap gate, and file generation) and jump directly to Phase 5 (wire conventions), then continue to Phase 6 (offer GitHub repo creation).
- **(u)**: Proceed to Phase 2 (full interview from scratch; both files will be overwritten on accept).
- **(r)**: Proceed to Phase 2 pre-filled from existing content; user amends rather than restarts.

**If one file exists:** Warn which file exists. Ask `<filename> already exists — overwrite it? (y/n)`. If no: skip generating that file only; continue with the other.

**If neither exists:** Proceed directly to Phase 2.

---

## Phase 2 — Interview

**If entering from Phase 1 `(r)efine`:** Open by showing the user what is already known from the existing files before asking any questions:

```
Based on your existing README.md and CLAUDE.md, here's what I have:

  Purpose:  [extracted value or "unclear"]
  Audience: [extracted value or "unclear"]
  Scope:    [extracted value or "unclear"]
  Tone:     [extracted value or "unclear"]
  Type:     [extracted value or "unclear"]

What would you like to change or add?
```

Ask only about gaps or changes the user raises — do not re-ask for values already present.

Generate abstract questions one at a time. Let the project context (directory name, any existing files, prior answers) inform which questions to ask — do not follow a fixed list. Good question domains: project purpose and goals, intended audience, scope and explicit out-of-scope boundaries, tone (serious vs. playful, strict vs. forgiving), whether this is a hobby or professional project.

**All answers are long-form free text.** Do not offer multiple-choice options during the interview.

After each answer, display an updated recap:

```
## Project Recap

**Purpose:** [what you've learned, or "unknown"]
**Audience:** [what you've learned, or "unknown"]
**Scope:**    [what you've learned, or "unknown"]
**Tone:**     [what you've learned, or "unknown"]
**Type:**     [hobby / professional / unknown]
```

Continue until Purpose, Audience, and Tone have no "unknown" — those three are required before moving to Phase 3. Scope and Type may be inferred if the user hasn't addressed them. Typically 4–6 questions suffice; stop when you can write the first sentence of the README without a placeholder.

When evaluating whether an answer is strong enough to accept, load [references/interview-guide.md](references/interview-guide.md).

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

Before writing, verify the recap gives a specific enough scope that a stranger can understand what this project does and doesn't do in one sentence. If not, prompt for one clarifying answer before generating.

Shape every decision from the recap: framing, tone, what's included and omitted. Consider these sections (not all required — include only what the recap warrants): project name and one-line purpose, who it's for, what it does and doesn't do, a tone-appropriate closing. A three-section README that matches the project's character is better than eight generic sections.

**CLAUDE.md** — write via Write tool.

Derive all conventions from the recap. Load [references/interview-guide.md](references/interview-guide.md) for the tone-to-voice translation table.

Include: 1–2 sentences of project purpose, coding philosophy derived from tone and seriousness, and any scope boundaries the agent should respect. Do not include technology-specific guidance.

**`.gitignore`** — ensure two entries are present: `settings.local.json` and `.weld/tmp/`.

Use Glob to check if `.gitignore` exists. If missing: create via Write tool with both entries on separate lines. If exists: read it, then append any missing entries on separate lines.

---

## Phase 5 — Wire gh-weld

Fetch conventions.md from upstream:

WebFetch: `https://raw.githubusercontent.com/WrathZA/github-weld/main/.weld/conventions.md`

Prompt: "Return the full raw file content verbatim, no summarization."

If fetch fails: output "Could not reach github-weld repo — check your connection. Run `/gh-weld-setup` again or wire manually." and skip to Phase 6.

Evaluate each target. Record a status: **add**, **update**, **skip**.

**`.weld/conventions.md`**:
- If file is missing → status: **add** (create from upstream)
- If file exists and content matches fetched content exactly → status: **skip**
- If file exists and content differs → status: **update** (note line counts: upstream N lines vs local M lines)

**`CLAUDE.md`** (`@.weld/conventions.md` line):
- Read the freshly-written CLAUDE.md
- If `@.weld/conventions.md` appears on any line → status: **skip**
- Otherwise → status: **add** (prepend as first line)

Display:

```
gh-weld wiring — planned changes:

  .weld/conventions.md  <status>
  CLAUDE.md             <status>

Proceed? (y/n)
```

If both are **skip**: output "gh-weld already wired." and skip to Phase 6.

If user answers n: skip to Phase 6.

Apply only **add** and **update** targets:

- `.weld/conventions.md` (add or update): if update, note "Updating conventions.md — upstream has N lines, local had M lines." Write fetched content via Write tool.
- `CLAUDE.md` (add): read current content, prepend `@.weld/conventions.md` followed by a blank line, write back via Write tool.

---

## Phase 6 — GitHub Repo (optional)

Check for an existing remote:

```bash
git remote -v > .weld/tmp/remotes.txt
```

Read `.weld/tmp/remotes.txt` with the Read tool. If the content contains `origin`, a remote already exists — run `rm .weld/tmp/remotes.txt` and skip silently.

If no `origin` remote exists, ask (single keypress):

```
No GitHub remote found — create one now? (y/n)
```

If yes: invoke `/gh-weld-repo` to create and push the repo. If `/gh-weld-repo` is not installed or fails, tell the user: "Install gh-weld and run `/gh-weld-repo` manually to create the GitHub repo."
If no: skip.

---

## Phase 7 — Done

Output a summary reflecting what was actually done in this run. Use the following labels:

- `written` — file was generated by Phase 4
- `(existing)` — file already existed; Phase 4 was skipped (Phase 1a path)
- `(skipped)` — file was skipped by user choice (one-file case)
- `wired` — conventions applied by Phase 5
- `(already wired)` — Phase 5 found both targets already up to date

```
Setup complete.

  README.md            <label>
  CLAUDE.md            <label>
  .weld/conventions.md <label>
```

If `/gh-weld-repo` was run, include the repo URL in the output.

Then ask (single keypress):

```
Close the loop? (y) run /gh-weld-adopt → /gh-weld-ship → /gh-weld-export  (n) skip
```

- **(y)**: invoke `/gh-weld-adopt`. When it completes, invoke `/gh-weld-ship`. When it completes, invoke `/gh-weld-export`. If any skill invocation fails or is not installed, output which step failed and stop — do not attempt subsequent steps.
- **(n)**: exit cleanly — no further output, no partial state.
