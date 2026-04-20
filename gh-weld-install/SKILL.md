---
name: gh-weld-install
description: Wire gh-weld into a target project: copies .weld/conventions.md from upstream, adds .weld/tmp/ to .gitignore, and adds @.weld/conventions.md to CLAUDE.md. Idempotent — skips files already up to date, shows diff before overwriting changed conventions. Use when setting up a new project to use gh-weld skills, or re-running on an existing project to check if conventions.md has drifted from upstream. Trigger phrases: "install gh-weld", "set up gh-weld", "wire up weld", "add gh-weld to this project".
compatibility: Requires Claude Code with WebFetch. Run from the target project root.
---

Wire gh-weld into the current project. Three idempotent operations; confirms before writing.

## NEVER

- **NEVER write any file without showing the plan and getting explicit confirmation first**
  **Instead:** Complete steps 1–3 (locate, fetch, diff) then show the full plan and wait for (y/n) before touching anything.
  **Why:** Running in the wrong directory silently corrupts an unrelated project's CLAUDE.md and .gitignore.

- **NEVER append to .gitignore or CLAUDE.md without checking for the exact line first**
  **Instead:** Search for `.weld/tmp/` and `@.weld/conventions.md` before appending; skip if already present.
  **Why:** Duplicate entries signal the skill isn't idempotent and create noisy diffs.

- **NEVER overwrite .weld/conventions.md without showing what changed**
  **Instead:** Compare fetched content to local; if different, output the line-count delta in the plan summary (step 4 handles the confirm).
  **Why:** The user may have made local edits; silent overwrite destroys them.

- **NEVER use `|` (pipe) in Bash calls**
  **Instead:** Redirect output to `.weld/tmp/<file>` with `>` and read back with the Read tool.
  **Why:** Claude Code stops execution silently when it encounters a pipe.
  Note: `|` in markdown table syntax is unaffected.

- **NEVER chain Bash calls with `&&` or `;`**
  **Instead:** Run each command as a separate Bash tool call.
  **Why:** Claude Code's safety check fires on multi-command calls and interrupts mid-flow.

- **NEVER use `$()` command substitution**
  **Instead:** Write content to a fixed path under `.weld/tmp/` with the Write tool instead of capturing output into variables.
  **Why:** Claude Code's permission system prompts on `$()` during execution, interrupting unnecessarily.

## Workflow

### 1 — Locate project root

Run:
```bash
git rev-parse --show-toplevel
```

If the command fails: output "Not inside a git repository — navigate to your project root and retry." and stop.

Note the path as `project_root`.

### 2 — Fetch conventions.md from upstream

WebFetch: `https://raw.githubusercontent.com/WrathZA/github-weld/main/.weld/conventions.md`

Prompt: "Return the full raw file content verbatim, no summarization."

Hold the result as `upstream_conventions`.

If fetch fails: output "Could not reach github-weld repo — check your connection and retry." and stop.

### 3 — Determine what will change

Evaluate each target. Record a status for each: **add**, **update**, **skip**.

**`.gitignore`**
- Read `<project_root>/.gitignore` (treat as empty if missing)
- If `.weld/tmp/` appears on any line → status: **skip**
- Otherwise → status: **add** (`append .weld/tmp/`)

**`.weld/conventions.md`**
- If file is missing → status: **add** (create from upstream)
- If file exists and content matches `upstream_conventions` exactly → status: **skip**
- If file exists and content differs → status: **update** (note line counts: upstream N lines vs local M lines)

**`CLAUDE.md`**
- Read `<project_root>/CLAUDE.md` (treat as empty if missing)
- If `@.weld/conventions.md` appears on any line → status: **skip**
- If file is missing → status: **add** (create with `@.weld/conventions.md`)
- Otherwise → status: **add** (prepend `@.weld/conventions.md` as first line)

### 4 — Show plan and confirm

Display:

```
gh-weld-install — planned changes in <project_root>:

  .gitignore            <status line>
  .weld/conventions.md  <status line>
  CLAUDE.md             <status line>

Proceed? (y/n)
```

If all three are **skip**: output "Already installed and up to date." and stop.

If user answers n: stop.

### 5 — Apply changes

Apply only **add** and **update** targets, in order.

**`.gitignore`** (if add):
- Read `<project_root>/.gitignore` with Read tool
- Append `.weld/tmp/` on its own line
- Write back with Write tool

**`.weld/conventions.md`** (if add or update):
- If update: note "Updating conventions.md — upstream has N lines, local had M lines."
- Write `upstream_conventions` to `<project_root>/.weld/conventions.md` with Write tool

**`CLAUDE.md`** (if add):
- Read `<project_root>/CLAUDE.md` with Read tool (empty string if missing)
- Prepend `@.weld/conventions.md` followed by a blank line, then the existing content
- Write back with Write tool

### 6 — Done

Output:
```
gh-weld-install complete.

Open a new Claude Code session in this project — conventions will load automatically.
```
