# GitHub Weld

Reusable GitHub workflow skills for Claude Code. Provides `gh-weld-issue`, `gh-weld-next`, `gh-weld-ship`, `gh-weld-export`, and `gh-weld-adopt` — a complete issue-to-merge loop using the `gh` CLI.

@.weld/conventions.md

## Dogfood the loop — never hand-roll git for changes to this repo

This repo *is* the gh-weld workflow. Every change to it must flow through the skills, not raw `git checkout -b` / `gh issue create`. Pick the entry point by *when* the work is tracked:

- **Implementing a change right now** (the common case here): do the work, then `/gh-weld-adopt` to create the issue + branch + commit in one step, then `/gh-weld-ship` to PR, squash-merge, close, and export. **Do not** use `/gh-weld-issue` for this — its first NEVER rule forbids same-session work.
- **Capturing work for later** (you won't implement it this session): `/gh-weld-issue` to file it. A future session runs `/gh-weld-next` → implement → `/gh-weld-ship`.
- **Picking up an existing open issue**: `/gh-weld-next <N>` to branch, implement, then `/gh-weld-ship`.

The canonical loop, in order: **`issue` *(defer)* or `adopt` *(now)* → `next` *(resume a filed issue)* → implement → `ship` → `export`.** If a skill can't be invoked mid-session (stale registry), execute its `SKILL.md` steps directly — that is still dogfooding. Reaching for plain `git checkout -b` is the one thing this repo exists to replace.

## skill-forge-* operations — **Critical: skills created outside this repo are lost to git**

**ALWAYS write new skill directories into this repo, never into `~/.claude/skills/` directly.** A skill created under `~/.claude/` is invisible to git and will never reach users — it exists only on your machine and is effectively lost.

When `skill-forge-create` or `write-a-skill` asks where to create the skill, provide a path inside this repo under `skills/` (e.g. `skills/gh-weld-newskill/` — never an absolute path with a hardcoded home dir). All skills live in the `skills/` directory; the repo ships as a single bundled plugin that auto-discovers them. If the tool does not prompt for a location, explicitly instruct it before it begins: "Write the skill to `skills/gh-weld-<name>/`."

Always create the skill on a branch, not on main — see conventions.md.

For all other `skill-forge-*` operations (`skill-forge-update`, `skill-forge-judge`, `skill-forge-recap`, etc.), always target the `SKILL.md` inside this repo — not the symlinked copy under `~/.claude/skills/`.

## Adding a new skill

After creating a new skill directory with a `SKILL.md` under `skills/` in this repo, run the symlink script so the skill is available globally:

```
bash symlink-global-skills.sh
```

Run from the repo root.

This links the new skill dir into `~/.claude/skills/`. The script is idempotent — safe to re-run at any time.