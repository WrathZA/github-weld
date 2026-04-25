#!/usr/bin/env bash
# Symlink all skill dirs in this repo into ~/.claude/skills/
# Safe to re-run — skips dirs that are already linked, skips non-skill dirs.
# Also removes dangling symlinks that point to skill dirs no longer in the repo.

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.claude/skills"

mkdir -p "$TARGET_DIR"

# Remove dangling symlinks whose target no longer exists
for link in "$TARGET_DIR"/*; do
  if [ -L "$link" ] && [ ! -e "$link" ]; then
    echo "removing stale symlink: $(basename "$link")"
    rm "$link"
  fi
done

for skill_dir in "$REPO_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"

  # Skip non-skill dirs (no SKILL.md inside)
  [ -f "$skill_dir/SKILL.md" ] || continue

  target="$TARGET_DIR/$skill_name"

  if [ -L "$target" ]; then
    echo "already linked: $skill_name"
  elif [ -e "$target" ]; then
    echo "skipped (exists, not a symlink): $skill_name"
  else
    ln -s "$skill_dir" "$target"
    echo "linked: $skill_name"
  fi
done
