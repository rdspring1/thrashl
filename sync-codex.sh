#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)/codex"
CODEX_DIR="$HOME/.codex"

mkdir -p "$CODEX_DIR/prompts" "$CODEX_DIR/scripts"

cp "$REPO_DIR/AGENTS.md" "$CODEX_DIR/AGENTS.md"
rsync -av --delete "$REPO_DIR/prompts/" "$CODEX_DIR/prompts/"
rsync -av --delete "$REPO_DIR/scripts/" "$CODEX_DIR/scripts/"
