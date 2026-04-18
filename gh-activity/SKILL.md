---
name: gh-activity
description: "GitHub activity digest — lists issues and PRs grouped by time window (today, last 3 days, last 7 days, last 30 days). Supports repo-scoped or GitHub-wide views, selected by single keypress. Use when: the user wants a repo overview, activity summary, recent activity digest, or to see what's changed. Trigger phrases: \"what's been happening\", \"activity digest\", \"repo overview\", \"recent activity\", \"what's new\"."
compatibility: Requires gh CLI authenticated (gh auth login). Designed for Claude Code.
---

# gh-activity

Activity digest grouped by recency. Fetch, bucket, render.

## NEVER

- **NEVER omit a time window because it has no activity**
  **Instead:** Show a `None` placeholder under Issues and PRs.
  **Why:** Omitting windows makes the digest look misleading — the user can't tell if nothing happened or the window was skipped.

- **NEVER use `|` (pipe) in Bash calls**
  **Instead:** Read JSON output directly from the tool result — no piping needed in this skill.
  **Why:** Claude Code stops execution when it encounters a pipe, interrupting the session without warning.
  Note: `|` in markdown table row syntax is unaffected.

- **NEVER chain Bash calls with `&&` or `;`**
  **Instead:** Run each command as a separate Bash tool call.
  **Why:** Claude Code's safety check fires on ambiguous multi-command calls and interrupts mid-flow.

- **NEVER use `$()` command substitution**
  **Instead:** Read command output directly from the Bash tool result.
  **Why:** Claude Code's permission system prompts on `$()` during execution, interrupting unnecessarily.

- **NEVER mix items across windows**
  **Instead:** Each item appears in exactly one window — the most recent it qualifies for.
  **Why:** Overlapping windows inflate counts and confuse the user about what's actually new.

## Workflow

### 1 — Scope

Ask: `Scope: (r)epo or (g)ithub-wide? [r]`

- `r` or Enter → current repo only
- `g` → all repos visible to the authenticated user

If the response is neither `r`, `g`, nor Enter: re-prompt once, then default to repo scope.

### 2 — Pre-flight

```bash
gh auth status
```

If this fails: output "gh is not authenticated — run `gh auth login` first." and stop.

Check gh version:

```bash
gh --version
```

`gh search` requires gh v2.29+. If the version is older and the user chose GitHub-wide scope, warn: "gh search requires v2.29 or later — falling back to repo scope." and proceed as repo scope.

### 3 — Fetch

**Repo scope:**

```bash
gh issue list --state all --limit 200 --json number,title,state,author,url,createdAt
```

```bash
gh pr list --state all --limit 200 --json number,title,state,author,url,createdAt
```

**GitHub-wide scope:**

```bash
gh search issues --limit 200 --sort created --json number,title,state,author,url,createdAt,repository
```

```bash
gh search prs --limit 200 --sort created --json number,title,state,author,url,createdAt,repository
```

Read the JSON from each tool result directly — no temp files needed.

> Discussions are not supported by the `gh` CLI JSON output; omit silently.

### 4 — Bucket

Get today's date (UTC). Classify each item into exactly one window:

| Window | Item's `createdAt` is on or after… |
|--------|-------------------------------------|
| Today | today 00:00 UTC |
| Last 3 days | today − 2 days 00:00 UTC |
| Last 7 days | today − 6 days 00:00 UTC |
| Last 30 days | today − 29 days 00:00 UTC |

Assign to the most recent qualifying window. Items older than 30 days are omitted.

### 5 — Render

```
## Today
### Issues
- #42 Fix login crash [open] — @alice — https://github.com/...
### Pull Requests
- #43 Add dark mode [merged] — @bob — https://github.com/...

## Last 3 days
### Issues
None
### Pull Requests
- #41 Bump deps [closed] — @carol — https://github.com/...

## Last 7 days
...

## Last 30 days
...
```

For **GitHub-wide scope**, prefix each item with the repo: `owner/repo#42 Title [state] — @author — url`.

Show item counts per window as a header suffix: `## Today (3 issues, 1 PR)`.
