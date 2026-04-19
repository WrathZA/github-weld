# github-weld 🪢

Claude Code skills that close the loop on every change — from issue to merge, with context captured at each step. The result is a structured delivery history your future self, your team, or an LLM can actually learn from.

These skills are opinionated about *workflow*, not implementation — they work alongside whatever you're building.

![github-weld workflow diagram](diagram.svg)

Git gives you data — diffs and commit hashes. GitHub gives you information — issues, PRs, linked references. `gh-weld` closes the gap toward knowledge: every merge carries a session export with the full reasoning trail, attached as a Gist and linked at the exact commit it belongs to. `git blame` a line, follow the PR, read why the decision was made and what was ruled out. That chain — from raw change to documented intent — is what turns a codebase into something a future agent or a new team member can actually learn from.

The payoff is cumulative. Run this loop consistently and each issue becomes a structured artifact: acceptance criteria up front, a correctly-named branch, a merged PR, and a session transcript capturing the context that never survives in commit messages alone. Over time that's a mineable decision history — not just what the code does, but why it does it that way.

## Skills

**[`/gh-weld-issue`](.claude/skills/gh-weld-issue/)** — Every piece of work needs an anchor before the first line of code. Creates one via a guided interview: duplicate check, structured body, and label discovery.

**[`/gh-weld-next`](.claude/skills/gh-weld-next/)** — Connecting intent to execution is where most workflows leak data. Picks an open issue, creates a correctly-named branch, and hands off to implementation.

**[`/gh-weld-ship`](.claude/skills/gh-weld-ship/)** — Shipping is the richest data moment in the delivery lifecycle. Wraps finished work in a PR, merges it, closes the issue, and exports session context.

**[`/gh-weld-export`](.claude/skills/gh-weld-export/)** — Git history captures what changed; session export captures why. Exports the Claude Code session as a Gist and posts a structured summary to any PR or issue.

**[`/gh-weld-adopt`](.claude/skills/gh-weld-adopt/)** — For when you started coding before creating an issue. Creates the issue retroactively, renames the branch, commits loose changes, and exports the session.

## Installation

Clone the repo and run the symlink script:

```bash
git clone https://github.com/WrathZA/github-weld
cd github-weld
bash symlink-global-skills.sh
```

This symlinks each skill directory into `~/.claude/skills/`, making them available in any project.

To update, pull and re-run the script — existing symlinks are left in place.

## Requirements

- [Claude Code](https://claude.ai/code)
- [gh CLI](https://cli.github.com/) authenticated (`gh auth login`)
- `git`
- `python3` (parses Claude Code session files to extract the conversation transcript for export to Gist)

## If a session goes off track

Sessions don't always follow the happy path. You pick an issue, notice a gap, file another issue, run a recap that misses the mark — and now the context window is loaded with things that aren't the task, but the conversation itself is worth keeping.

The pattern: **export before you clear.**

```
/gh-weld-export → target the issue you were working on
/clear
/gh-weld-next → pick the same issue → read the export comment for context
```

`/gh-weld-export` works with issues, not just PRs. The session becomes a comment on the issue — discoverable, linkable, mineable later. The Gist holds the full transcript with line anchors to every key decision.

This is the broader philosophy behind gh-weld: data you don't capture now is context you can never recover. A session export costs 30 seconds. The reasoning trail it preserves is the difference between a codebase you can learn from and one you can only read.

## Conventions

Claude Code's permission and safety systems have non-obvious interactions with shell execution — pipes, heredocs, and inline `gh` arguments all cause problems in practice. [`.weld/conventions.md`](.weld/conventions.md) documents the patterns these skills follow so you don't have to rediscover them when extending or contributing.
