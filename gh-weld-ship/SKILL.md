---
name: gh-weld-ship
description: "GitHub shipping loop — wraps your finished work in a PR, merges it, exports the session as a Gist, and posts it as a comment. Enriches the linked issue before closing — updates acceptance criteria checkboxes and posts a close-out narrative comment automatically. Does not implement code; you do the work, gh-weld-ship handles everything GitHub. Use when you're ready to open a PR, merge, and export context."
disable-model-invocation: true
---

# gh-weld-ship

You wrote the code. gh-weld-ship ships it.

Creates a PR with context, squash-merges, closes the linked issue, exports the session to a Gist, and posts it on the PR.

## NEVER

- NEVER create a PR from main — `gh pr create` will succeed but target the wrong base, shipping unreleased work directly; create a feature branch first
- NEVER pass a PR body with `#`-prefixed lines as an inline `--body` argument — write to `.weld/tmp/pr-body.md` and pass via `--body-file`
- NEVER merge before confirming the PR was created successfully — a failed `gh pr create` still exits 0 in some cases; verify the URL is present in the output before calling `gh pr merge`
- NEVER close the issue before the merge is confirmed
- NEVER skip the Gist export — the session context on the PR is the audit trail
- NEVER prompt the user during issue enrichment — derive checkboxes and close-out narrative from the Step 3 synthesis automatically; any prompt here breaks the single-keypress ship flow
- NEVER chain Bash commands with `&&` or `;` — Claude Code's safety check fires on multi-command calls and interrupts mid-flow; run each as a separate Bash tool call
- NEVER use `|` (pipe) in Bash tool calls — Claude Code stops execution on pipe; redirect to a temp file with `>` and read back with the Read tool
- NEVER use `$()` command substitution — Claude Code's permission system prompts on `$()` during execution; use fixed paths under `.weld/tmp/` instead
- NEVER use bash heredoc (`cat > file << 'EOF'`) for content with `#`-prefixed lines — headers trigger Claude Code's security check on every execution; use the Write tool instead
- NEVER use `echo >` or `cat` to write file content — use the Write tool; it avoids shell escaping issues and doesn't trigger permission checks
- NEVER use `find`, `grep`, or `cat` as Bash commands — use Glob, Grep, and Read tools instead; they are faster, safer, and don't require shell permissions

## Workflow

### 1 — Validate branch

```bash
git branch --show-current
```

If the result is `main` or `master`: output "You're on main — /gh-weld-adopt can help. It'll create an issue for what you're working on, rename the branch, and get everything tracked before you ship." and stop.

### 2 — Find the linked issue

Try to infer the issue number from the branch name. Common patterns: `fix/42-slug`, `feat/42-slug`, `issue-42`, `42-slug`. Extract the number if present.

If no number can be inferred, ask: "Which issue does this branch implement? Enter a number or (n)one."

If an issue number is known, read it:
```bash
gh issue view <N> --json number,title,body,state
```
If the issue is already closed, warn: "Issue #N is already closed — continue anyway? (y/n)"

### 3 — Summarize the work

Before synthesizing, ask: do the commits fully represent the delivered work, or are there staged/unstaged changes not yet committed? If loose changes exist, warn: "There are uncommitted changes on this branch — commit them before shipping, or they won't be included in the PR."

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

Read the PR URL from the output (e.g. `https://github.com/owner/repo/pull/7`). Extract the PR number from the URL. Write the full PR URL to `.weld/tmp/pr-url.txt` and just the PR number to `.weld/tmp/pr-number.txt` with the Write tool.

Clean up:
```bash
rm .weld/tmp/pr-body.md
```

### 5 — Squash merge

```bash
gh pr merge --squash --delete-branch
```

If the merge fails, diagnose the cause (merge conflict → resolve and retry; branch protection → check required reviews or status checks; stale ref → sync branch and retry) and attempt to fix it. If unresolvable, surface the error and ask "(r)etry / (Q)uit?" — do not proceed to Step 6 until the merge is confirmed.

Once merge is confirmed, switch to main:
```bash
git checkout main
```

If that fails (repo uses `master`):
```bash
git checkout master
```

### 6 — Enrich and close the issue

If there is a linked issue, perform the following automatically — no user prompts:

**a. Update acceptance criteria checkboxes**

The issue body was fetched in Step 2. The commits and changed files were read in Step 3. For each `- [ ]` criterion in the issue body, determine whether the delivered changes satisfy it. A criterion is satisfied if a commit message or changed file directly addresses the named behaviour; when ambiguous, leave it unchecked and note the uncertainty in the close-out comment.

If the issue body contains no `- [ ]` criteria, skip the edit step.

Otherwise, write the updated body with satisfied items marked `- [x]` to `.weld/tmp/issue-updated-body.md` using the Write tool:

```bash
gh issue edit <N> --body-file .weld/tmp/issue-updated-body.md
```

If `gh issue edit` fails, diagnose and fix: malformed body → rewrite the temp file with corrected content; auth error → verify with `gh auth status`; issue locked → note it and skip. Keep retrying until no further fixes apply, then surface the error and ask "(s)kip / (Q)uit?"

```bash
rm .weld/tmp/issue-updated-body.md
```

**b. Post a close-out comment**

Using the synthesis from Step 3, write the close-out comment to `.weld/tmp/issue-close-comment.md` using the Write tool:

```markdown
<One sentence describing what the PR delivered.>

**What changed:**
- <meaningful change 1 — what and why>
- <meaningful change 2 — what and why>

Shipped in PR #<PR number>.
```

```bash
gh issue comment <N> --body-file .weld/tmp/issue-close-comment.md
```

If `gh issue comment` fails, diagnose and fix: malformed body → rewrite the temp file; auth error → verify with `gh auth status`; rate limit → wait and retry. Keep retrying until no further fixes apply, then surface the error and ask "(s)kip / (Q)uit?"

```bash
rm .weld/tmp/issue-close-comment.md
```

**c. Close the issue**

```bash
gh issue close <N>
```

### 7 — Export session to Gist and post to PR

Read `.weld/tmp/pr-number.txt` with the Read tool to get the PR number. Clean up:
```bash
rm .weld/tmp/pr-number.txt
```

Invoke `/gh-weld-export` with the PR number as context. This exports the session transcript, uploads it as a secret Gist, and posts a structured summary comment on the merged PR.

If `/gh-weld-export` fails, warn: "Session export failed — ship is otherwise complete." and continue to the completion output.

Read `.weld/tmp/pr-url.txt` with the Read tool to get the PR URL. Clean up:
```bash
rm .weld/tmp/pr-url.txt
```

Output:
```
Shipped: <issue title>

PR:    <pr-url>
Issue: https://github.com/<owner>/<repo>/issues/<N> (closed)
```
