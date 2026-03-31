#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)/claude"
CLAUDE_DIR="$HOME/.claude"

mkdir -p "$CLAUDE_DIR/commands" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills"

rsync -av --delete "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
rsync -av --delete "$REPO_DIR/commands/" "$CLAUDE_DIR/commands/"
rsync -av --delete "$REPO_DIR/agents/" "$CLAUDE_DIR/agents/"
