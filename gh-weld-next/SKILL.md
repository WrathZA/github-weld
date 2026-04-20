---
name: gh-weld-next
description: "Pick an open GitHub issue to work on, then create a branch and hand off to the user. Lists open issues, lets you select one, reads the full issue details, optionally adds context notes posted as an issue comment, creates a branch, and confirms you're ready to implement. Pair with /gh-weld-ship when work is done. Use when: starting a new piece of work, picking the next issue from the backlog, adding notes or context to an issue before branching, or annotating an issue with decisions before starting work."
---

# gh-weld-next

Find something to work on. Read it. Branch. Go.

## NEVER

- NEVER pick a blocked issue (one whose blocker issues are still open) without warning the user — starting blocked work wastes the sprint and may require a branch rename when the blocker resolves
- NEVER create a branch from main if main has uncommitted changes — uncommitted changes contaminate the new branch and pollute the issue diff. Instead: commit or stash first.

## Workflow

### 1 — Check working tree

```bash
git status --porcelain
```

If dirty: output "Working tree has uncommitted changes — commit or stash before starting new work." and stop.

```bash
git branch --show-current
```

If not on `main` or `master`: warn "You're on branch `<branch>` — switch to main before starting new work? (y/n)". If yes:
```bash
git checkout main
```

Pull latest:
```bash
git pull
```

### 2 — List open issues

```bash
gh issue list --state open --json number,title,labels,updatedAt
```

Display as a numbered menu. For each issue show: `N. #<number> — <title> [<labels>]`. Sort by issue number ascending.

If no open issues: output "No open issues. Run /gh-weld-issue to create one." and stop.

### 3 — Pick

Ask: "Which issue? Enter a number from the list, or describe what you want to work on."

If the user describes something: match against titles and confirm before proceeding. If no match, offer to run `/gh-weld-issue` first.

Read the full issue:
```bash
gh issue view <N> --json number,title,body,labels
```

Display the full title and body so the user can read the acceptance criteria.

Check for blockers: look for `Depends on #` or `Blocked by #` in the body. If found, fetch each referenced issue:
```bash
gh issue view <blocker-N> --json number,title,state
```

If any blocker is still open: warn "Issue #N is blocked by open issue #<blocker> — <title>. Work on it anyway? (y/n)". If no, return to step 3.

Ask: "(a)ccept, (r)evise, or (s)kip?"

- **(a)**: proceed to step 4.
- **(r)**: prompt "Add context or notes (send as a single message):". Good notes: scope changes, key decisions, ambiguity resolved. Skip: restating the issue body. Collect the user's input. Write it to `.weld/tmp/comment-body.md` via Write tool. Post with:
  ```bash
  gh issue comment <N> --body-file .weld/tmp/comment-body.md
  ```
  Delete with `rm .weld/tmp/comment-body.md`. Proceed to step 4.
- **(s)**: return to "Which issue?" prompt in step 3.

### 4 — Create branch

Infer a branch name from the issue title: lowercase, hyphens, max 50 chars. Prefix with `fix/` for bugs, `feat/` for features, `chore/` for chores — inferred from labels. If type is ambiguous, use no prefix.

Show the proposed name and ask: "(a)ccept or enter a different name?"

```bash
git checkout -b <branch-name>
```

### 5 — Hand off

Output:
```
Ready. You're on branch `<branch-name>` — issue #<N> is waiting.

When you're done: /gh-weld-ship
```

Stop. The user implements. `/gh-weld-ship` picks it up from here.
