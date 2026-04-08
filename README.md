# thrashl

**Reduce thrash. Increase signal.**

thrashl is a lightweight control layer for working with coding agents.

It turns Claude (or any agent) from a drifting conversation into a predictable system using:
- explicit modes
- stop conditions
- high-signal handoffs

The goal is simple:
**less guessing, fewer loops, faster progress.**

---

## Core idea

Most agent workflows fail because of thrash:
- repeated guesses
- unclear next steps
- bloated context
- no clean stopping point

thrashl fixes this by enforcing:

- **mode switching** → `/impl`, `/debug`, `/vet`, `/save`
- **early stopping** → don’t let agents guess forever
- **decision outputs** → every step produces something actionable

---

## Commands

- `/impl` → make a minimal change
- `/debug` → form hypotheses and pick one experiment
- `/vet` → skeptical review + high-value tests
- `/save` → write a clean markdown handoff

You don’t need all of them.

Even just `/debug` or `/save` will help.

---

## Installation

```bash
mkdir -p ~/.claude/commands ~/.claude/agents
./sync-claude.sh
```

To keep `~/.claude` in sync after updates:

```bash
./sync-claude.sh
```

> `sync-claude.sh` rsyncs `claude/commands/` and `claude/agents/` into `~/.claude/`. Copy `claude/CLAUDE.md` to `~/.claude/CLAUDE.md` manually if desired.

---

## Codex CLI

Codex CLI is supported too.

The Codex port keeps the same control model:
- bounded implementation
- hypothesis-first debugging
- evidence discipline
- replayable state in `save.md`

But it uses Codex-native surfaces instead of imitating Claude commands:
- `AGENTS.md` as the main doctrine file
- prompt templates instead of slash commands
- small helper scripts where deterministic behavior is better than prompting

Install it with:

```bash
mkdir -p ~/.codex
./sync-codex.sh
```

To keep `~/.codex` in sync after updates:

```bash
./sync-codex.sh
```

> `sync-codex.sh` copies `codex/AGENTS.md` plus `codex/prompts/` and `codex/scripts/` into `~/.codex/`.
