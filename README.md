# github-weld

Reusable GitHub workflow skills for Claude Code. Welds your GitHub workflows together — a complete issue-to-merge loop using the `gh` CLI.

## Skills

| Skill | What it does |
|-------|-------------|
| `/gh-weld-issue` | Create a GitHub issue via guided interview — duplicate check, structured body, label discovery |
| `/gh-weld-next` | Pick an open issue, create a branch, hand off to implementation |
| `/gh-weld-ship` | Wrap finished work in a PR, squash-merge, close the issue, export session context |
| `/gh-weld-export` | Export the current session as a Gist and post a structured summary comment to a PR or issue |
| `/gh-weld-adopt` | Retroactively formalize ad-hoc work — create an issue, rename the branch, commit loose changes, export session |

The intended flow is:

```
/gh-weld-issue  →  /gh-weld-next  →  (implement)  →  /gh-weld-ship
```

`/gh-weld-export` runs automatically at the end of `/gh-weld-ship`, or standalone when you want to post session context to any PR or issue.

`/gh-weld-adopt` is the escape hatch — use it when you started coding before creating an issue.

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
- `python3` (for session export)

## Conventions

See [`.weld/conventions.md`](.weld/conventions.md) for the shell execution rules these skills follow — covers `gh` body-file patterns, temp file paths, and Claude Code permission system gotchas.
