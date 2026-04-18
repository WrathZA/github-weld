---
name: gh-weld-issue
description: "Create a GitHub issue via guided interview. Checks for duplicates before creation (c/u/d resolution: continue as new, use existing and stop, or drop). Collects title and type; constructs structured body from scope, acceptance criteria, and blockers. Infers blockers from open issues. Discovers and applies repo labels. Enforces verifiable acceptance criteria (each must name a command, visible change, or measurable value). Creates via gh CLI using --body-file. One issue per outcome — never batches multiple ideas. Use when: filing a bug, planning a feature, capturing a task, or creating any GitHub issue. Skip if you are about to implement the work in this session — use gh-weld-ship instead."
---

# gh-weld-issue

Create a new GitHub issue through a brief HITL interview.

## NEVER

- NEVER pass a body with `#`-prefixed lines as an inline `--body` argument — write to `.weld/tmp/issue-body.md` with the Write tool and pass via `--body-file`; headers trigger Claude Code's security check on every execution
- NEVER skip the duplicate check — a missed duplicate creates noise and confusion in the backlog
- NEVER create issues for work you are about to implement in the same session — use `gh-weld-ship` instead; it creates the issue and links it to the branch automatically
- NEVER batch multiple ideas into one issue — one issue, one merge, one audit trail; batched issues can't be independently closed or reverted
- NEVER chain Bash commands with `&&` or `;` — Claude Code's safety check fires on multi-command calls and interrupts mid-flow; run each as a separate Bash tool call
- NEVER use `|` (pipe) in Bash tool calls — Claude Code stops execution on pipe; redirect to a temp file with `>` and read back with the Read tool. Note: `|` in markdown table syntax is unaffected.
- NEVER use `$()` command substitution or backtick substitution (`` `cmd` ``) — Claude Code's permission system prompts on both during execution; use fixed paths under `.weld/tmp/` instead
- NEVER use bash heredoc (`cat > file << 'EOF'`) for content with `#`-prefixed lines — headers trigger Claude Code's security check; use the Write tool instead
- NEVER use `echo >` or `cat` to write file content — use the Write tool
- NEVER use `find`, `grep`, or `cat` as Bash commands — use Glob, Grep, and Read tools instead

## Workflow

### Phase 1 — Discover

1. Ask: "What are you trying to build or fix?"

2. From the response, infer:
   - A candidate title (specific, action-oriented: "Add X", "Fix Y when Z")
   - Type: **bug** / **feature** / **task** / **chore**

3. Run a duplicate check using 2–4 key terms extracted from the inferred title:
   ```bash
   gh issue list --search "<key terms>" --state all --json number,title,state,updatedAt
   ```
   - If the result is non-empty: display each as `#N — Title [OPEN]` or `#N — Title [CLOSED, X days]` (compute age from `updatedAt`)
   - If open duplicates exist, show:
     ```
     Possible match(es):
       #N — Title [OPEN]

     (c)ontinue as new, (u)se existing, (d)rop?
     ```
     - **(c)** — proceed
     - **(u)** — output the issue URL and stop; `gh-weld-issue` creates issues, not edits them
     - **(d)** — stop
   - If only closed matches: show them for context, offer `(c)ontinue / (d)rop`
   - If empty: proceed silently

4. Ask 1–2 follow-up questions to fill remaining gaps — one at a time. Stop when title, type, and scope are clear.

5. Show the recap:
   ```
   Title: <title>
   Type:  <bug|feature|task|chore>
   Scope: <one sentence>
   ```
   Ask: "Does this look right?" Loop until confirmed.

### Phase 2 — Lock in

6. **Acceptance criteria** — draft from scope context, show as a numbered list, ask for additions/corrections. Each criterion must name a verifiable state: a command that exits 0, a visible change, a value that differs. Push back on unverifiable criteria.

7. **Blockers** — list open issues:
   ```bash
   gh issue list --state open --json number,title,labels
   ```
   Infer likely blockers from the scope. If none are obvious, ask once: "Does this depend on any open issues? Enter numbers or (n)one."

### Phase 3 — Create

8. Determine labels to apply. At minimum, apply the type label if it exists in the repo:
   ```bash
   gh label list --json name
   ```
   Match `bug`, `enhancement`, `feature`, `task`, `chore` against what exists. Note matching labels for step 9.

9. Use the Write tool to write the issue body to `.weld/tmp/issue-body.md`:

   ```markdown
   ## Summary

   <scope sentence>

   ## Acceptance Criteria

   - [ ] <criterion 1>
   - [ ] <criterion 2>

   ## Blockers

   <"None" or "Depends on #N, #M">

   ---
   *Created with [gh-weld](https://github.com/WrathZA/github-weld)*
   ```

10. Create the issue:
    ```bash
    gh issue create --title "<title>" --body-file .weld/tmp/issue-body.md --label "<labels>"
    ```
    If no matching labels exist, omit `--label`.

11. Clean up and output the issue URL:
    ```bash
    rm .weld/tmp/issue-body.md
    ```
    Output the URL. Done.
