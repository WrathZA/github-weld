---
name: gh-weld-export
description: "Export the current Claude Code session as a markdown transcript and post it as a comment on a GitHub PR or issue. Reads the session JSONL file from ~/.claude/projects/, uploads a full transcript as a secret Gist, and posts a structured summary comment with deep-link anchors. Use when: posting session context to a PR after merge, saving conversation history, uploading a session transcript to GitHub, documenting what we did, or when the user says 'export context', 'post context to PR/issue', 'export the session', or 'post session to GitHub'."
---

# gh-weld-export

Export the current session and post it to a GitHub PR or issue as a structured comment with a Gist link.

## Workflow

**If invoked by another skill** (e.g. `gh-weld-ship` after merge), the caller passes the PR or issue number as context. Use it directly.

**If invoked standalone** with no number: ask "Which PR or issue number should I post to?"

### Steps

1. Export the session transcript:
   ```bash
   python3 .claude/skills/gh-weld-export/scripts/export-session.py --out .weld/tmp/session-export.md
   ```

2. Upload as a secret Gist:
   ```bash
   gh gist create --filename "session-export.md" .weld/tmp/session-export.md > .weld/tmp/gist-url.txt
   ```
   Read `.weld/tmp/gist-url.txt` with the Read tool to get `<gist-url>`.

3. From session memory, identify 5–10 key events. Include an event if it answers "so what?" for a future reader:
   - A design or approach decision was made
   - An issue was created, closed, or had its state changed
   - A blocker was encountered or resolved
   - A constraint or non-obvious fact was discovered
   - A file was created or significantly restructured (not just edited)

   Exclude: read-only exploration, repeated failed attempts, minor formatting/cleanup changes, file reads with no outcome.

4. For each key event, find its line number in the transcript:
   ```bash
   grep -n "<distinctive string from event>" .weld/tmp/session-export.md
   ```
   Run each grep as a separate Bash call. If no match, include the entry without a line anchor.

5. Use the Write tool to write the summary to `.weld/tmp/export-summary.md`:
   ```markdown
   ## Session Summary

   - **<event description>** — [line N](<gist-url>#file-session-export-md-LN)
   ```
   The Gist anchor format for `session-export.md` is `#file-session-export-md-L<N>`.

6. Read the first 100 lines of `.weld/tmp/session-export.md` with the Read tool (`limit: 100`) as the inline snippet.

7. Use the Write tool to write the comment body to `.weld/tmp/export-comment.md`:
   ```markdown
   ## Session Summary

   - **<event>** — [line N](<gist-url>#file-session-export-md-LN)
   ...

   ---

   <first 100 lines of transcript>

   ---

   [Full session context](<gist-url>)

   ---
   *Created with [gh-weld](https://github.com/WrathZA/github-weld)*
   ```

8. Post the comment:
   - For a PR:
     ```bash
     gh pr comment <number> --body-file .weld/tmp/export-comment.md
     ```
   - For an issue:
     ```bash
     gh issue comment <number> --body-file .weld/tmp/export-comment.md
     ```

9. Clean up:
   ```bash
   rm .weld/tmp/session-export.md .weld/tmp/export-comment.md .weld/tmp/export-summary.md
   ```

   If invoked by another skill (caller mode), **do not delete `.weld/tmp/gist-url.txt`** — leave it for the caller to read and remove. If invoked standalone, also remove it:
   ```bash
   rm .weld/tmp/gist-url.txt
   ```

## NEVER

- NEVER use `--last N` except as `--last 1` to isolate a single oversized exchange when debugging — it drops session history and defeats the purpose of the export
- NEVER override `--max-chars` above 65536 — the default of 60000 is a practical cap for readability
- NEVER run the script from a directory other than the project root — the project key is inferred from `$PWD`
- NEVER batch multiple grep lookups in one Bash call — each event lookup must be a separate call; Claude Code's safety check fires on multi-command calls and interrupts the session mid-flow
- NEVER post to an issue when the caller said PR, or vice versa — confirm the type if ambiguous; `gh pr comment` on an issue number silently succeeds but posts to the wrong thread
- NEVER omit the `[Full session context](<gist-url>)` link from the comment even if the gist upload appeared to partially succeed — a broken anchor is better than a missing one

## Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `No session directory found` | Wrong CWD or project not opened in Claude Code | Run from project root; verify `~/.claude/projects/<key>/` exists |
| `No session files found` | Session directory empty | Try again after at least one exchange |
| `No messages found in session` | JSONL exists but has no user/assistant messages | New or interrupted session |
| `gh gist create` fails | Rate limit, auth, or network error | Post the first 100 lines of the transcript inline with note: "Full transcript unavailable — Gist upload failed"; omit Gist links from the summary |

## Do NOT load

`scripts/` — invoked via Bash only; do not read as context
