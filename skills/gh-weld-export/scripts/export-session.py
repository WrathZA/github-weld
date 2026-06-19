#!/usr/bin/env python3
"""
Export the current Claude Code session as a markdown transcript.

Usage:
  python3 export-session.py [--out FILE] [--last N]

  --out FILE    Write output to FILE instead of stdout
  --last N      Only include the last N user/assistant exchanges (default: all)

The current project session is inferred from $PWD.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

def project_key(cwd: str) -> str:
    """Convert a directory path to Claude Code's project key format."""
    return cwd.replace("/", "-")

def find_session_file(cwd: str) -> Path:
    key = project_key(cwd)
    sessions_dir = Path.home() / ".claude" / "projects" / key
    if not sessions_dir.exists():
        raise FileNotFoundError(f"No session directory found for {cwd}\n  Looked in: {sessions_dir}")
    jsonl_files = list(sessions_dir.glob("*.jsonl"))
    if not jsonl_files:
        raise FileNotFoundError(f"No session files found in {sessions_dir}")
    return max(jsonl_files, key=lambda p: p.stat().st_mtime)

def format_tool_call(name: str, inp: dict) -> str:
    """Format a tool call as a collapsible GitHub markdown block."""
    # Pick a representative snippet to show in the summary line
    snippet = ""
    if name in ("Bash", "Read", "Write", "Edit", "Glob", "Grep"):
        key = {"Bash": "command", "Read": "file_path", "Write": "file_path",
               "Edit": "file_path", "Glob": "pattern", "Grep": "pattern"}.get(name)
        if key and key in inp:
            snippet = f": `{str(inp[key])[:80]}`"
    body = json.dumps(inp, indent=2)
    return f"<details><summary>🔧 {name}{snippet}</summary>\n\n```json\n{body}\n```\n\n</details>"


def extract_text(content) -> str:
    """Extract plain text from a message content field (string or list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "thinking":
                    pass  # skip internal thinking blocks
                elif block.get("type") == "tool_use":
                    name = block.get("name", "tool")
                    inp = block.get("input", {})
                    parts.append(format_tool_call(name, inp))
                elif block.get("type") == "tool_result":
                    pass  # omit tool results
        return "\n\n".join(p for p in parts if p)
    return str(content)

def load_exchanges(session_file: Path):
    exchanges = []
    with open(session_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") not in ("user", "assistant"):
                continue
            if obj.get("isMeta"):
                continue
            role = obj["type"]
            msg = obj.get("message", {})
            content = extract_text(msg.get("content", ""))
            if not content.strip():
                continue
            ts = obj.get("timestamp", "")
            exchanges.append({"role": role, "content": content, "ts": ts})
    return exchanges

def format_markdown(exchanges, session_file: Path, last: int | None) -> str:
    if last is not None:
        # Count pairs: keep last N user messages and their assistant replies
        user_indices = [i for i, e in enumerate(exchanges) if e["role"] == "user"]
        if last < len(user_indices):
            cutoff = user_indices[-last]
            exchanges = exchanges[cutoff:]

    n_exchanges = sum(1 for e in exchanges if e["role"] == "user")
    exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "# 📋 Session Export",
        "",
        "| | |",
        "|---|---|",
        f"| **File** | `{session_file.name}` |",
        f"| **Exported** | {exported_at} |",
        f"| **Exchanges** | {n_exchanges} |",
        "",
        "---",
        "",
    ]
    for entry in exchanges:
        if entry["role"] == "user":
            icon, label = "🧑", "User"
        else:
            icon, label = "🤖", "Assistant"
        ts_sub = f" <sub>{entry['ts']}</sub>" if entry["ts"] else ""
        lines.append(f"#### {icon} {label}{ts_sub}")
        lines.append("")
        lines.append(entry["content"].strip())
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Export Claude Code session as markdown")
    parser.add_argument("--out", help="Output file path (default: stdout)")
    parser.add_argument("--last", type=int, help="Only last N user exchanges")
    parser.add_argument("--max-chars", type=int, default=60000,
                        help="Truncate output to fit within N chars by dropping oldest exchanges (default: 60000)")
    parser.add_argument("--cwd", help="Project directory (default: $PWD)")
    args = parser.parse_args()

    cwd = args.cwd or os.environ.get("PWD", os.getcwd())
    try:
        session_file = find_session_file(cwd)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    exchanges = load_exchanges(session_file)
    if not exchanges:
        print("No messages found in session.", file=sys.stderr)
        sys.exit(1)

    md = format_markdown(exchanges, session_file, args.last)

    # Trim from the oldest exchange until output fits within --max-chars
    user_indices = [i for i, e in enumerate(exchanges) if e["role"] == "user"]
    while len(md) > args.max_chars and len(user_indices) > 1:
        user_indices = user_indices[1:]
        trimmed = exchanges[user_indices[0]:]
        md = format_markdown(trimmed, session_file, None)
    if len(md) > args.max_chars:
        print(f"Warning: output ({len(md)} chars) exceeds --max-chars ({args.max_chars}) even after trimming all but the last exchange.", file=sys.stderr)

    if args.out:
        Path(args.out).write_text(md)
        print(f"Written to {args.out} ({len(md)} chars)", file=sys.stderr)
    else:
        print(md)

if __name__ == "__main__":
    main()
