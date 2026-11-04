#!/bin/bash
# Install Claude Code skills/agents/hooks to personal scope (~/.claude/)
# profile ando (starbase) の CLAUDE.md は ~/.config/claude/profiles/ando/ に link する
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

echo "==> Installing hooks"
mkdir -p "$CLAUDE_DIR/hooks"
for hook in "$DOTFILE_DIR/claude/hooks/"*; do
  name=$(basename "$hook")
  target="$CLAUDE_DIR/hooks/$name"
  if [ -L "$target" ]; then
    current=$(readlink "$target")
    if [ "$current" = "$hook" ]; then
      echo "  [ok] $name (already linked)"
    else
      echo "  [WARN] $name -> $current (different target, leaving alone)"
    fi
  elif [ -e "$target" ]; then
    echo "  [WARN] $name exists as non-symlink, leaving alone"
  else
    ln -s "$hook" "$target"
    echo "  [link] $name"
  fi
done

echo "==> Installing CLAUDE.md"
claude_md_src="$DOTFILE_DIR/claude/CLAUDE.md"
claude_md_target="$CLAUDE_DIR/CLAUDE.md"
if [ -f "$claude_md_src" ]; then
  if [ -L "$claude_md_target" ]; then
    current=$(readlink "$claude_md_target")
    if [ "$current" = "$claude_md_src" ]; then
      echo "  [ok] CLAUDE.md (already linked)"
    else
      echo "  [WARN] CLAUDE.md -> $current (different target, leaving alone)"
    fi
  elif [ -e "$claude_md_target" ]; then
    echo "  [WARN] CLAUDE.md exists as non-symlink, leaving alone"
  else
    ln -s "$claude_md_src" "$claude_md_target"
    echo "  [link] CLAUDE.md"
  fi
fi

# settings.json は link せず、共有の claude/settings.json と、マシン固有の
# ~/.claude/settings.machine.json（dotfile には入れない）を合成して作る。
# Claude Code はユーザー全体の設定として ~/.claude/settings.json しか読まないため。
# 作った後に Claude Code 側で書き換わった場合は上書きしない。
echo "==> Installing settings.json (shared + settings.machine.json)"
settings_src="$DOTFILE_DIR/claude/settings.json"
settings_machine="$CLAUDE_DIR/settings.machine.json"
settings_target="$CLAUDE_DIR/settings.json"
settings_mark="$CLAUDE_DIR/.settings.generated.sha256"
if [ -f "$settings_src" ]; then
  if ! command -v jq >/dev/null 2>&1; then
    echo "  [WARN] jq not found, skipping settings.json"
  else
    settings_tmp=$(mktemp)
    machine_in="$settings_machine"
    if [ ! -f "$machine_in" ]; then
      machine_in=$(mktemp)
      echo '{}' > "$machine_in"
    fi
    jq -n --slurpfile shared "$settings_src" --slurpfile machine "$machine_in" \
      -f "$DOTFILE_DIR/claude/scripts/merge-settings.jq" > "$settings_tmp"
    new_sum=$(shasum -a 256 "$settings_tmp" | cut -d' ' -f1)
    write_settings=false
    if [ -L "$settings_target" ]; then
      rm "$settings_target"
      write_settings=true
    elif [ -e "$settings_target" ]; then
      current_sum=$(shasum -a 256 "$settings_target" | cut -d' ' -f1)
      if [ "$current_sum" = "$new_sum" ]; then
        echo "  [ok] settings.json (up to date)"
      elif [ -f "$settings_mark" ] && [ "$current_sum" = "$(cat "$settings_mark")" ]; then
        write_settings=true
      else
        echo "  [WARN] settings.json was changed after it was generated, leaving alone"
        echo "         move the changes into settings.machine.json or claude/settings.json, delete settings.json, and run again"
      fi
    else
      write_settings=true
    fi
    if [ "$write_settings" = true ]; then
      mv "$settings_tmp" "$settings_target"
      chmod 600 "$settings_target"
      echo "$new_sum" > "$settings_mark"
      echo "  [generate] settings.json"
    else
      rm -f "$settings_tmp"
    fi
  fi
fi

echo "==> Installing profile CLAUDE.md (profile: ando / starbase)"
profile_md_src="$DOTFILE_DIR/claude/profiles/ando/CLAUDE.md"
profile_md_target="$HOME/.config/claude/profiles/ando/CLAUDE.md"
if [ -f "$profile_md_src" ]; then
  mkdir -p "$(dirname "$profile_md_target")"
  if [ -L "$profile_md_target" ]; then
    current=$(readlink "$profile_md_target")
    if [ "$current" = "$profile_md_src" ]; then
      echo "  [ok] profiles/ando/CLAUDE.md (already linked)"
    else
      echo "  [WARN] profiles/ando/CLAUDE.md -> $current (different target, leaving alone)"
    fi
  elif [ -e "$profile_md_target" ]; then
    echo "  [WARN] profiles/ando/CLAUDE.md exists as non-symlink, leaving alone"
  else
    ln -s "$profile_md_src" "$profile_md_target"
    echo "  [link] profiles/ando/CLAUDE.md"
  fi
fi

echo "==> Installing .tmux.conf"
tmux_src="$DOTFILE_DIR/tmux/.tmux.conf"
tmux_target="$HOME/.tmux.conf"
if [ -f "$tmux_src" ]; then
  if [ -L "$tmux_target" ]; then
    current=$(readlink "$tmux_target")
    if [ "$current" = "$tmux_src" ]; then
      echo "  [ok] .tmux.conf (already linked)"
    else
      echo "  [WARN] .tmux.conf -> $current (different target, leaving alone)"
    fi
  elif [ -e "$tmux_target" ]; then
    echo "  [WARN] .tmux.conf exists as non-symlink, leaving alone"
  else
    ln -s "$tmux_src" "$tmux_target"
    echo "  [link] .tmux.conf"
  fi
fi

echo ""
echo "Done. Restart Claude Code to pick up new skills/agents/CLAUDE.md."
