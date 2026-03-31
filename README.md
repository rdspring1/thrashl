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
mkdir -p ~/.claude
cp -r claude/commands ~/.claude/
cp -r claude/agents ~/.claude/
cp claude/CLAUDE.md ~/.claude/CLAUDE.md
```
