---
name: gh-adopt
description: "Retroactively formalizes ad-hoc in-progress work — reads session context and git state, creates a structured GitHub issue, creates or renames a branch to match repo conventions, commits loose changes, pushes, and exports the session as a Gist comment on the new issue. Works from any branch including main (moves uncommitted changes or ahead-commits to a new branch). Use when: you started work without creating an issue first, or when the user says 'adopt this work', 'create an issue for what we're doing', 'formalize this branch', 'retroactively track this', 'adopt this cleanup', 'adopt this chore'."
compatibility: Requires git and gh CLI. Designed for Claude Code.
---

# gh-adopt

You did the work first. gh-adopt creates the paper trail.

## NEVER

- **NEVER proceed adoption from `main` when working tree is clean and no commits are ahead of `origin/main`**
  **Instead:** Output "Nothing to adopt — working tree is clean and main is up to date." and stop.
  **Why:** There is genuinely nothing to adopt — adoption requires loose work to formalize.

- **NEVER create the issue before confirming the summary with the user**
  **Instead:** Show the synthesized summary and proposed issue body; wait for (a)ccept before calling `gh issue create`.
  **Why:** The issue is permanent. A wrong title or misattributed scope creates backlog noise that outlasts the session.

- **NEVER commit without showing what will be staged**
  **Instead:** Display `git status --porcelain` output and ask "(a)ccept / (s)kip" before staging anything.
  **Why:** Unintended files (`.env`, build artifacts) committed here will be pushed and visible in the GitHub issue thread.

- **NEVER pass a body with `#`-prefixed lines as an inline `--body` argument**
  **Instead:** Write to `.weld/tmp/adopt-issue-body.md` with the Write tool and pass via `--body-file`.
  **Why:** `#`-prefixed lines trigger Claude Code's security check on every execution, interrupting the agent mid-flow.

- **NEVER skip deleting the old remote branch after rename**
  **Instead:** After pushing the new branch name, run `git push origin --delete <old-name>` if the old remote existed.
  **Why:** GitHub shows both branches as linked to the issue — the stale name creates ambiguity in the development sidebar.

- **NEVER skip the session export**
  **Instead:** Always invoke `/gh-export` with the new issue number as context after pushing.
  **Why:** The Gist comment is the audit trail — it proves what was already done before the issue was created.

## Workflow

### 1 — Handle if on main

```bash
git branch --show-current
```

If the result is `main` or `master`:

Check for uncommitted changes:

```bash
git status --porcelain
```

Check for commits ahead of remote:

```bash
git log origin/main..HEAD --oneline
```

**If neither has output:** output "Nothing to adopt — working tree is clean and main is up to date." and stop.

**If uncommitted changes exist:**

Inspect existing branch names to infer naming convention:

```bash
git branch -a
```

Propose a branch name (lowercase, hyphens, max 50 chars, using the repo's prefix convention). Show it and ask: "(a)ccept or enter a different name?"

```bash
git checkout -b <branch-name>
```

Continue to Step 2.

**If commits are ahead of `origin/main`:**

Inspect existing branch names:

```bash
git branch -a
```

Propose a branch name. Show it and ask: "(a)ccept or enter a different name?"

Create the branch at the current HEAD, reset main, then check out the new branch:

```bash
git branch <branch-name>
```

```bash
git reset --hard origin/main
```

```bash
git checkout <branch-name>
```

Continue to Step 2.

### 2 — Read working state

Run each as a separate Bash call:

```bash
git status --porcelain
```

```bash
git log main..HEAD --oneline
```

```bash
git diff main..HEAD --name-only
```

Save the current branch name — you'll need it to detect and delete the old remote after renaming.

### 3 — Synthesize and confirm

From **session context** (what has been discussed and built in this conversation) and the git output above, synthesize:

- A proposed issue title (one line, imperative mood)
- The work type (bug / feature / chore) — use this to frame the issue title and acceptance criteria; for the branch prefix, use whatever pattern was inferred from `git branch -a` above
- A structured issue body (see template below)

Before naming the type, inspect the repo's existing branch names to infer the local convention:

```bash
git branch -a
```

Look for patterns in existing branches (e.g. `fix/`, `feat/`, `feature/`, `bugfix/`, `chore/`, no prefix at all). Match whatever convention the repo already uses. If no pattern is apparent, use no prefix. Do not impose a convention the repo hasn't adopted.

Show the synthesis to the user:

```
Here's what I see you working on:

**Title:** <proposed title>
**Type:** <bug / feature / chore>

**Body preview:**
<body>

(a)ccept / (e)dit / (q)uit
```

- `a` — proceed to Step 4
- `e` — user provides corrections; update and loop
- `q` — abort

**Issue body template:**

```markdown
## Summary

<2–3 sentence description of what is being built and why>

## Acceptance Criteria

- [ ] <verifiable criterion — names a command, visible change, or measurable value>

## Blockers

None
```

Acceptance criteria must be verifiable. Reject vague entries like "works correctly" — they must name a command, visible change, or measurable value.

### 4 — Create the issue

Write the confirmed body to `.weld/tmp/adopt-issue-body.md` using the Write tool.

Apply the appropriate label if it exists in the repo:

```bash
gh label list
```

Create the issue, redirecting output to capture the URL:

```bash
gh issue create --title "<title>" --label "<label>" --body-file .weld/tmp/adopt-issue-body.md > .weld/tmp/adopt-issue-url.txt
```

If the label doesn't exist, omit `--label`.

Read `.weld/tmp/adopt-issue-url.txt` with the Read tool to get the issue URL. Extract the issue number from the URL (it appears as `.../issues/<N>`).

Clean up:

```bash
rm .weld/tmp/adopt-issue-body.md
rm .weld/tmp/adopt-issue-url.txt
```

### 5 — Commit uncommitted changes

Check for loose work:

```bash
git status --porcelain
```

If output is non-empty, show it and ask:

```
These changes will be committed and pushed:
<git status output>

(a)ccept / (s)kip
```

If accepted:

```bash
git add .
```

```bash
git commit -m "adopt: capture in-progress work for issue #<N>"
```

### 6 — Rename the branch

Construct the new branch name using the prefix convention inferred from `git branch -a` (Step 3), the issue number, and a slug derived from the issue title. Slug rules: lowercase, hyphens only, max 40 chars.

Check whether the current branch has a remote tracking branch:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

If this succeeds, record the old remote branch name (strip the `origin/` prefix). If it fails (no upstream), there's nothing to delete after rename.

Rename locally:

```bash
git branch -m <new-branch-name>
```

### 7 — Push

```bash
git push -u origin <new-branch-name>
```

If an old remote branch existed, delete it:

```bash
git push origin --delete <old-branch-name>
```

### 8 — Export session

Invoke `/gh-export` with the issue number as context. This exports the current session transcript, uploads it as a secret Gist, and posts a structured summary comment on the issue.

### 9 — Output

```
Adopted.

Issue:  <issue-url>
Branch: <new-branch-name>
```

Done.

## Errors

| Situation | Action |
|-----------|--------|
| `git log main..HEAD` is empty (branch exists but no commits) | Warn "Branch has no commits ahead of main — loose changes only. Continue? (y/n)" |
| `gh issue create` fails | Surface the error; do not rename the branch or push (nothing to link to yet) |
| `git push --delete` fails on old remote name | Warn "Could not delete old remote branch `<name>` — delete it manually via GitHub." and continue |
| `git branch -m` fails because new name already exists | Output the conflict and ask the user for an alternative branch name |
| `/gh-export` fails | Warn "Session export failed — adopt is otherwise complete." and output issue URL and branch name |
