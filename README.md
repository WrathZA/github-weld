# github-weld 🪢

Git records *what* changed. `gh-weld` captures *why* and *how*.

Every commit is a data point. A linked issue with acceptance criteria is information. A session export is knowledge: the reasoning, trade-offs, and decisions behind the code. `gh-weld` closes that chain automatically, at every merge.

The skills enforce a workflow, not a tech stack. They work with whatever you're building.

## How it works

Git gives you data: diffs and commit hashes. GitHub gives you information: issues, PRs, linked references. `gh-weld` closes the gap to knowledge: every merge carries a session export with the full reasoning trail, attached as a Gist at the exact commit it belongs to. `git blame` a line, follow the PR, read why the decision was made and what was ruled out.

![github-weld workflow diagram](diagram.svg)

The payoff compounds. Run this loop and each issue becomes a structured artifact: acceptance criteria up front, a correctly-named branch, a merged PR, and a session transcript with the context commit messages never hold. Over time, you have a decision history: not just what the code does, but why.

## Skills

**[`/gh-weld-issue`](.claude/skills/gh-weld-issue/):** Work without a tracking anchor leaks context. Creates a structured issue via a guided interview: duplicate check, acceptance criteria, and label discovery.

**[`/gh-weld-next`](.claude/skills/gh-weld-next/):** The gap between intent and execution is where context gets lost. Picks an open issue, creates a correctly-named branch, and hands off to implementation.

**[`/gh-weld-ship`](.claude/skills/gh-weld-ship/):** A merge captures more context than any other moment in the delivery cycle, and it's the most likely to go undocumented under pressure. Wraps finished work in a PR, squash-merges it, closes the linked issue, and exports the session as a Gist attached to the merge.

**[`/gh-weld-export`](.claude/skills/gh-weld-export/):** The reasoning behind a decision lives in the session. Once the context window is cleared, it's gone. Exports the Claude Code session as a Gist and posts a structured summary comment to any PR or issue.

**[`/gh-weld-adopt`](.claude/skills/gh-weld-adopt/):** Ad-hoc work without an issue disappears from the history. Retroactively creates a structured issue, renames the branch to match, commits loose changes, and exports the session.

## Installation

The skills form a single loop — install all of them. A partial install leaves the workflow broken at the step you skipped.

**Via Claude Code plugin marketplace** (no clone required):

```
/plugin marketplace add WrathZA/github-weld
/plugin install gh-weld-issue
/plugin install gh-weld-next
/plugin install gh-weld-ship
/plugin install gh-weld-export
/plugin install gh-weld-adopt
/plugin install gh-weld-activity
```

**Via symlink script** (for local development or if you prefer cloning):

```bash
git clone https://github.com/WrathZA/github-weld
cd github-weld
bash symlink-global-skills.sh
```

This symlinks each skill directory into `~/.claude/skills/`, making them available in any project. To update, pull and re-run the script — existing symlinks are left in place.

## Requirements

- [Claude Code](https://claude.ai/code) (or equivalent AI coding agent, untested with others)
- [gh CLI](https://cli.github.com/) authenticated (`gh auth login`)
- `git`
- `python3` (used by `/gh-weld-export` to parse session files and generate the transcript Gist)

## If a session goes off track

Sessions stray. You pick an issue, notice a gap, file another, run a recap that misses. Now the context window holds more than the task. The conversation itself is worth keeping.

The pattern: **export before you clear.**

```
/gh-weld-export → target the issue you were working on
/clear
/gh-weld-next → pick the same issue → read the export comment for context
```

`/gh-weld-export` works with issues, not just PRs. The session becomes a comment on the issue: discoverable, linkable, mineable later. The Gist holds the full transcript with line anchors to every key decision.

The principle: context not captured now is gone. A session export costs 30 seconds. The reasoning trail it preserves is the difference between a codebase you can learn from and one you can only read.

## Conventions

Claude Code's permission and safety systems have non-obvious interactions with shell execution: pipes, heredocs, and inline `gh` arguments all cause problems in practice. [`.weld/conventions.md`](.weld/conventions.md) documents the hard-won patterns these skills follow, so you don't have to rediscover them when extending or contributing.
