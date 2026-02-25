# load-context skill

## Purpose
Builds a context block from toolkit files and copies it to clipboard.
Paste into any new Claude conversation to restore full project context
without re-explaining history, conventions, or open work.

## Usage
```bash
context
```
Or run directly:
```bash
source ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit/skills/load-context/load-context.sh
```

## Keyboard Shortcut
**⌘⇧C** — Opens Terminal and runs `context` automatically.
Set up via Automator Quick Action (saved as "Load Context" in Services).

## Alias
`context` — defined in ~/.zshrc on MacBook Pro M1.

## Modes
- **1. Quick** — orientation block only (~300 words). Covers owner, machines, conventions, active skills, open work, recent completions. Use this 90% of the time.
- **2. Full** — Quick block + all active project files + skills inventory. Use when starting a complex session that spans multiple projects.

## How it works
1. Reads hardcoded orientation block (conventions, structure, open work)
2. In Full mode, appends all files from /projects and skills-inventory.md
3. Copies combined block to clipboard via pbcopy
4. Paste directly into Claude chat

## Keeping it current
The Quick orientation block is hardcoded in the script. Update it when:
- A project completes (move to Recent Completions, remove from Open Work)
- A new skill is added (add to Active Skills)
- A convention changes

The Full mode pulls live from /projects and skills-inventory.md — those update automatically as you maintain those files.
