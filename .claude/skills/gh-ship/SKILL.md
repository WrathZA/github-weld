---
name: gh-ship
description: "GitHub shipping loop — wraps your finished work in a PR, merges it, exports the session as a Gist, and posts it as a comment. Does not implement code; you do the work, gh-ship handles everything GitHub. Invoke as /gh-ship to ship the current branch, or /gh-ship <issue-number> to target a specific issue. Use when you're ready to open a PR, merge, and export context."
---

# gh-ship

You wrote the code. gh-ship ships it.

Creates a PR with context, squash-merges, closes the linked issue, exports the session to a Gist, and posts it on the PR.

## NEVER

- NEVER create a PR from main — validate the branch first; stop if on main
- NEVER pass a PR body with `#`-prefixed lines as an inline `--body` argument — write to `.weld/tmp/pr-body.md` and pass via `--body-file`
- NEVER merge before confirming the PR was created successfully
- NEVER close the issue before the merge is confirmed
- NEVER skip the Gist export — the session context on the PR is the audit trail

## Workflow

### 1 — Validate branch

```bash
git branch --show-current
```

If the result is `main` or `master`: output "Cannot ship from main — create a feature branch first." and stop.

### 2 — Find the linked issue

Try to infer the issue number from the branch name. Common patterns: `fix/42-slug`, `feat/42-slug`, `issue-42`, `42-slug`. Extract the number if present.

If no number can be inferred, ask: "Which issue does this branch implement? Enter a number or (n)one."

If an issue number is known, read it:
```bash
gh issue view <N> --json number,title,body,state
```
If the issue is already closed, warn: "Issue #N is already closed — continue anyway? (y/n)"

### 3 — Summarize the work

Read the commits on this branch since it diverged from main:
```bash
git log main..HEAD --oneline
```

Read the list of changed files:
```bash
git diff main..HEAD --name-only
```

From the commit messages, changed files, and (if available) the issue body, synthesize:
- A 1–3 sentence summary of what was implemented
- A bullet list of meaningful changes (what changed and why, not just filenames)
- A minimal test plan (how to verify the main behaviour)

### 4 — Create the PR

Use the Write tool to write the PR body to `.weld/tmp/pr-body.md`:

```markdown
## Summary

<1–3 sentence description of what was implemented>

## Changes

- <change 1 — what and why>
- <change 2 — what and why>

## Test plan

- [ ] <how to verify the main behaviour>

## Issue

Closes #<N>
```

If there is no linked issue, omit the `## Issue` section.

Create the PR:
```bash
gh pr create --title "<issue title or branch description>" --body-file .weld/tmp/pr-body.md --base main
```

Read the PR number from the output (it appears as part of the URL, e.g. `.../pull/7`). Write just the PR number to `.weld/tmp/pr-number.txt` with the Write tool.

Clean up:
```bash
rm .weld/tmp/pr-body.md
```

### 5 — Squash merge

```bash
gh pr merge --squash --delete-branch
```

### 6 — Close the issue

If there is a linked issue:
```bash
gh issue close <N> --comment "Shipped in PR #<PR number>."
```

### 7 — Export session to Gist and post to PR

Read `.weld/tmp/pr-number.txt` with the Read tool to get the PR number. Clean up:
```bash
rm .weld/tmp/pr-number.txt
```

Invoke `/gh-export` with the PR number as context. This exports the session transcript, uploads it as a secret Gist, and posts a structured summary comment on the merged PR.

Done.
