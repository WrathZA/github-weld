---
name: gh-repo
description: Create a GitHub repo from a local directory via `gh repo create`. Inspects the current directory to infer repo name, language, topics, .gitignore template, and license — then interviews the user only for what it cannot infer, one question at a time. Shows a full confirm/edit/abort summary before acting. Pushes the local repo to the new remote on confirm. Use when: starting a project that needs a GitHub remote, pushing a local directory to GitHub for the first time. Triggers: "create a repo", "push to GitHub", "new GitHub repo", "initialize remote", "set up GitHub".
compatibility: Requires git and gh CLI with authentication
---

# gh-repo

Create a GitHub repo from a local directory — infer what you can, ask for the rest, confirm before acting.

## NEVER

- **NEVER chain bash commands with `&&` or `;`**
  **Instead:** One command per Bash tool call.
  **Why:** Claude Code's safety system fires on ambiguous multi-command calls and interrupts the session mid-flow.

- **NEVER use `|` (pipe) in Bash tool calls**
  **Instead:** Redirect output to a file under `.weld/tmp/` with `>` and read it back with the Read tool.
  **Why:** Claude Code stops execution when it encounters a pipe — no error, no warning, the agent just halts mid-flow. Note: `|` in markdown table cell syntax is unaffected.

- **NEVER use `$(...)` command substitution inside bash commands**
  **Instead:** Run the command as a standalone Bash call and reference the output in subsequent steps.
  **Why:** Claude Code's permission system prompts on `$()` during execution.

- **NEVER call `gh repo create` before the confirm gate in Phase 3**
  **Instead:** Always show the full settings summary and receive `c` before acting.
  **Why:** Repo creation is hard to undo — wrong name or visibility requires deletion and recreation.

- **NEVER skip checking for an existing remote before adding one**
  **Instead:** Run `git remote -v` and read the output before `git remote add origin`.
  **Why:** Adding a duplicate remote fails with an error and leaves the repo in a broken state.

- **NEVER pass a multiline body containing `#`-prefixed lines as an inline `gh` argument**
  **Instead:** Write to a temp file (e.g. `.claude/tmp/repo-desc.md`) with the Write tool and pass via `--body-file`.
  **Why:** Headers in inline strings trigger an un-suppressible Claude Code permission prompt.

- **NEVER use `find`, `grep`, or `cat` in Bash tool calls**
  **Instead:** Use Glob to find files, Grep to search content, and Read to read files.
  **Why:** Built-in tools have tighter permissions and don't trigger Claude Code safety prompts the way raw shell commands can.

---

## Phase 1 — Inspect

Infer the repo name from the current directory's folder name (`pwd`). Use Glob to detect the stack:

| Indicator file | Stack | `.gitignore` template |
|---|---|---|
| `package.json` | Node.js | `Node` |
| `go.mod` | Go | `Go` |
| `Cargo.toml` | Rust | `Rust` |
| `pyproject.toml` or `requirements.txt` | Python | `Python` |
| `pom.xml` or `build.gradle` | Java | `Java` |
| `Gemfile` | Ruby | `Ruby` |

If a `LICENSE` file exists, read the first line to infer the license identifier (e.g. `MIT`, `Apache-2.0`).

If `git remote -v` shows `origin` is already configured: warn the user and ask `(c)ontinue anyway / (a)bort`. On abort, stop.

Note whether `git status` reports "not a git repository" — needed in Phase 4.

---

## Phase 2 — Interview

Before asking questions: check whether the inferred repo name looks right at `github.com/<username>/<name>`. Generic names (`test`, `project`, `new`, `app`, `demo`) are red flags — flag the name as a suggestion to reconsider and move it to question #5.

Ask only for settings still marked `(ask)`. Show inferred values first so the user can accept or override. One question at a time.

**Order:**
1. Visibility: "Public or private? [public]"
2. Description: "One-line repo description?"
3. License (only if no LICENSE file found): "License? (e.g. MIT, Apache-2.0, none) [none]"
4. Topics: "Suggested topics: `<detected stack>`. Accept, or enter your own?"
5. Name (only if user wants to override): "Repo name? [<inferred>]"

---

## Phase 3 — Confirm

Display the full settings summary:

```
Name:        <name>
Visibility:  <public|private>
Description: <description>
Topics:      <topics>
.gitignore:  <template>
License:     <license>
```

Ask: `(c)onfirm / (e)dit / (a)bort`

- `e` → ask "Which setting to change?" and loop back to Phase 2 for that field only
- `a` → output "Aborted. No changes made." and stop
- `c` → proceed to Phase 4

---

## Phase 4 — Create & Push

### Create the repo

Run as separate Bash calls (no chaining):

```bash
gh repo create <name> --<public|private> --description "<description>" --gitignore "<template>"
```

If a license was specified (not `none`):
```bash
gh repo create <name> --<public|private> --description "<description>" --gitignore "<template>" --license "<license>"
```

If the command fails:
- Output contains "Name already taken" → return to Phase 2, ask for a different name, and retry
- Output contains "authentication" or "401" → tell the user to run `gh auth login` and retry
- Any other error → surface the raw error output and stop

If topics were collected, set them after creation:
```bash
gh repo edit <owner>/<name> --add-topic "<topic>"
```

One `gh repo edit` call per topic.

### Initialize if needed

If Phase 1 noted "not a git repository": run `git init`, then `git add -A`, then `git commit -m "Initial commit"`. If the repo already has commits, skip the add/commit.

### Add remote and push

Read the repo URL from the `gh repo create` output. If no `origin` remote exists, run `git remote add origin <url>`. Push with `git push -u origin main`; if it fails because the default branch is `master`, retry with `git push -u origin master`.

---

## Phase 5 — Done

Output:
```
Repo created: <url>
Remote:       origin → <url>
Branch:       <branch> is now tracking origin/<branch>
```
