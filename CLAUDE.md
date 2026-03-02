# Claude Toolkit — Master Context File

## Who I Am
This toolkit belongs to Flint. I work across two machines:
- MacBook Pro M1 (primary)
- direct-lighting (terminal-only, transitional)

## What This Toolkit Is
A portable, version-controlled library of skills, prompts, subagents, and 
project documents that supports my use of Claude Code for automations, 
research, and workflow efficiencies.

## How This Toolkit Works
- Primary working copy lives in iCloud Drive (local-first)
- GitHub (private repo) is version control and backup — pushed deliberately
- All files are plain markdown (.md)
- Must run terminal-friendly on both machines — no GUI dependencies

## Working Conventions
- Always start with a plan before building anything
- Every project gets a single combined PRD + Plan file in /projects
- File naming: topic-YYYY-MM (e.g. claude-toolkit-2026-02)
- Skills are tracked in /skills-registry/skills-inventory.md
- The bible/master-reference.md is the living manual — update it as skills develop
- CHANGELOG.md lives at root — log meaningful additions and changes

## My Priorities
1. Local-first — minimize unnecessary API calls
2. Portable — everything works on a new machine within 15 minutes
3. Owned — prefer skills we control over borrowed dependencies
4. Simple — don't over-engineer; one layer of complexity at a time

## Folder Structure
- /bible — living manual and reference
- /projects — combined PRD + plan files, one per project
- /skills-registry — inventory of all skills across machines
- /prompts — reusable prompt templates
- /claude-md-templates — CLAUDE.md starters for new projects
- /subagents — specialist agent definitions

## API Keys
Never hardcode API keys in any file. Always use the prompt-on-entry 
method or environment variables. See skills-registry for the API key 
management skill.

## End-of-Session Updates

When asked to update toolkit documentation:
- session-context.md — top-level context, keep concise, dated completion blocks
- skills-registry/skills-inventory.md — one entry per skill, use established table format
- bible/master-reference.md — reusable lessons only, no session-specific detail
- CHANGELOG.md — reverse chronological, one entry per date, bullet format
- Always stage but never commit — Flint reviews and commits manually
- Make targeted edits only — do not rewrite sections that don't need changing

## Current Active Skills
See /skills-registry/skills-inventory.md for full list.
