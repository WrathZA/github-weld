---
name: gh-weld-repo
description: Create a GitHub repo from a local directory via `gh repo create`. Inspects the current directory to infer repo name, language, topics, .gitignore template, license, and description (from README.md when present) — then interviews the user only for what it cannot infer, one question at a time. Shows a full confirm/edit/abort summary before acting. Pushes the local repo to the new remote on confirm — on a fresh repo, bootstraps the scaffold on a branch so the first work lands via PR. Use when: starting a project that needs a GitHub remote, pushing a local directory to GitHub for the first time. Triggers: "create a repo", "push to GitHub", "new GitHub repo", "initialize remote", "set up GitHub".
compatibility: Requires git and gh CLI with authentication
---

# gh-weld-repo

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
  **Instead:** Write to a temp file (e.g. `.weld/tmp/repo-desc.md`) with the Write tool and pass via `--body-file`.
  **Why:** Headers in inline strings trigger an un-suppressible Claude Code permission prompt.

- **NEVER use `find`, `grep`, or `cat` in Bash tool calls**
  **Instead:** Use Glob to find files, Grep to search content, and Read to read files.
  **Why:** Built-in tools have tighter permissions and don't trigger Claude Code safety prompts the way raw shell commands can.

- **NEVER use `mktemp` or `$(mktemp ...)`**
  **Instead:** Use a fixed path under `.weld/tmp/` with the Write tool.
  **Why:** `mktemp` uses platform-dependent `/tmp/` paths, and the `$()` substitution it requires triggers Claude Code permission prompts.

- **NEVER offer Enter (empty line) as the way to accept a default in a prompt**
  **Instead:** Bind every default to an explicit keypress (e.g. `(n) none`, reply `k` to keep) — never `[default]`/"press Enter".
  **Why:** Claude Code's CLI can't submit an empty line, so an Enter-default is unreachable and the user is stuck.

- **NEVER commit the scaffold straight to `main` on a fresh bootstrap**
  **Instead:** Keep gh's initial commit (the `--gitignore`/`--license` files) as the base on `main`, then create a branch and commit the scaffold there.
  **Why:** A scaffold landed directly on `main` bypasses branch → PR → merge review and leaves `gh-weld-adopt` nothing to formalize, dead-ending the close-the-loop chain (issue #84).

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

Use Glob to check for `README.md`. If found, Read it and extract the first complete sentence from the first paragraph after any leading `#` heading (a sentence ends at `.`, `!`, or `?`) — this is the inferred description. If no sentence terminator is found, use the first line. If the result exceeds 120 characters, truncate at the nearest word boundary before the limit. If no `README.md` exists, or the file contains only a heading with no body paragraph, or the extracted text is empty after stripping whitespace, the inferred description is blank. Store this value for Phase 2.

If `git remote -v` shows `origin` is already configured: warn the user and ask `(c)ontinue anyway / (a)bort`. On abort, stop.

Note whether `git status` reports "not a git repository" — needed in Phase 4.

---

## Phase 2 — Interview

Before asking questions, think about what makes these settings good, not just valid: a repo name should be specific and searchable (someone scanning a repo list should guess what it does); a description should say what the project *is* and who it's for in one line, not restate the name; topics should be discovery terms others would actually search. Let that shape what you suggest and what you flag for reconsideration.

Check whether the inferred repo name looks right at `github.com/<username>/<name>`. Generic names (`test`, `project`, `new`, `app`, `demo`) are red flags — flag the name as a suggestion to reconsider and move it to question #5.

Ask only for settings still marked `(ask)`. Show inferred values first so the user can accept or override. One question at a time.

**Order:**
1. Visibility: "Public or private? Reply (p)ublic or pri(v)ate." Map `p`→public, `v`→private. Public is the recommended default — reply `p` to accept it. Do not rely on Enter; require a keypress.
2. Description: If an inferred description exists (from Phase 1), show `"Description: [<inferred>] — accept or enter a new one?"`. If blank, ask `"One-line repo description?"`.
3. License (only if no LICENSE file found): present a single-keypress menu:
   ```
   License? Single keypress:
     (m) MIT
     (a) Apache-2.0
     (g) GPL-3.0
     (b) BSD-3-Clause
     (i) ISC
     (p) MPL-2.0
     (u) Unlicense
     (n) none
   ```
   Map the keypress to the license identifier:
   `m`→`MIT`, `a`→`Apache-2.0`, `g`→`GPL-3.0`, `b`→`BSD-3-Clause`, `i`→`ISC`, `p`→`MPL-2.0`, `u`→`Unlicense`, `n`/Enter→`none`. The selected identifier is passed to `gh repo create --license "<id>"` in Phase 4 (omit `--license` entirely when `none`).
4. Topics: "Suggested topics: `<detected stack>`. Accept, or enter your own?"
5. Name (only if user wants to override): "Repo name? Reply `k` to keep `<inferred>`, or type a new name." Do not rely on Enter to accept the inferred name.

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

> On a fresh repo, the scaffold goes on a branch, not straight to `main` — the first body of work must flow through branch → PR → merge like every other change. Committing it to `main` bypasses review and dead-ends `gh-weld-adopt` (see the NEVER rule, ref #84).

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

If topics were collected, set them after creation. The `gh repo create` output names the new repo as `<owner>/<name>` (e.g. "✓ Created repository alice/my-app on GitHub") and the repo URL is `https://github.com/<owner>/<name>` — take `<owner>/<name>` from there; do not guess the owner.
```bash
gh repo edit <owner>/<name> --add-topic "<topic>"
```

One `gh repo edit` call per topic. If a call fails, log the error and continue — topic tagging is non-critical and should not block the push.

### Initialize if needed — graft onto the remote base

When Phase 1 noted "not a git repository", the repo gh just created already carries a minimal base commit on `main` — the `--gitignore`/`--license` files form GitHub's initial commit. Use **that** as the base and stack the scaffold on a branch on top of it. Do **not** create a second local initial commit: pushing it would be rejected as unrelated history. Run as separate Bash calls:

```bash
git init
```
```bash
git remote add origin <url>
```
```bash
git fetch origin
```
```bash
git reset --mixed origin/main
```
```bash
git branch -M main
```
```bash
git checkout -b setup/scaffold
```
```bash
git add -A
```
```bash
git commit -m "Scaffold project files"
```

`git reset --mixed origin/main` adopts gh's base commit as local `main` while leaving the scaffold files untouched in the working tree; the scaffold then lands as one commit on `setup/scaffold`. If the repo already has commits, skip this block — see "Existing history" below.

### Add remote and push

Read the repo URL from the `gh repo create` output (used as `<url>` above).

**Fresh bootstrap** (the Initialize block above ran): the remote is already added and local `main` already matches gh's base commit — push only the scaffold branch:

```bash
git push -u origin setup/scaffold
```

`main` stays the default branch and PR base; `setup/scaffold` carries the reviewable scaffold.

**Existing history** (Initialize block skipped): if no `origin` remote exists, run `git remote add origin <url>`. Because gh initialized the remote with a base commit, reconcile before pushing so the histories aren't unrelated:

```bash
git fetch origin
```
```bash
git pull --rebase origin main
```
```bash
git push -u origin <current-branch>
```

Determine `<current-branch>` with `git branch --show-current` (handles `main`, `master`, or any default without guessing). If the rebase reports conflicts, resolve them before pushing.

---

## Phase 5 — Done

**Fresh bootstrap:**
```
Repo created: <url>
Remote:       origin → <url>
Base:         main — gh's initial commit (.gitignore/license), the PR base
Scaffold:     setup/scaffold — your project files (provisional; /gh-weld-adopt renames it)

Next: run /gh-weld-adopt → /gh-weld-ship to open a PR, squash-merge, and close.
```

**Existing history:**
```
Repo created: <url>
Remote:       origin → <url>
Branch:       <branch> is now tracking origin/<branch>
```
