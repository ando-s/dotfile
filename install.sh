#!/bin/bash
# Install Claude Code skills/agents to personal scope (~/.claude/)
# Idempotent: safe to run multiple times. Existing files are not overwritten.

set -e

DOTFILE_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents"

echo "==> Installing skills"
for skill in "$DOTFILE_DIR/claude/skills/"*/; do
  name=$(basename "$skill")
  target="$CLAUDE_DIR/skills/$name"
  if [ -L "$target" ]; then
    current=$(readlink "$target")
    if [ "$current" = "${skill%/}" ]; then
      echo "  [ok] $name (already linked)"
    else
      echo "  [WARN] $name -> $current (different target, leaving alone)"
    fi
  elif [ -e "$target" ]; then
    echo "  [WARN] $name exists as non-symlink, leaving alone"
  else
    ln -s "${skill%/}" "$target"
    echo "  [link] $name"
  fi
done

echo "==> Installing agents"
for agent in "$DOTFILE_DIR/claude/agents/"*.md; do
  name=$(basename "$agent")
  target="$CLAUDE_DIR/agents/$name"
  if [ -L "$target" ]; then
    current=$(readlink "$target")
    if [ "$current" = "$agent" ]; then
      echo "  [ok] $name (already linked)"
    else
      echo "  [WARN] $name -> $current (different target, leaving alone)"
    fi
  elif [ -e "$target" ]; then
    echo "  [WARN] $name exists as non-symlink, leaving alone"
  else
    ln -s "$agent" "$target"
    echo "  [link] $name"
  fi
done

echo ""
echo "Done. Restart Claude Code to pick up new skills/agents."
