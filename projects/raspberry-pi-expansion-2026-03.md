# Raspberry Pi Expansion + AI Hedge Fund

**Document status:** Closed
**Date started:** 2026-03-01
**Date completed:** 2026-03-01
**Owner:** Flint  

---

## One-Line Goal

Connect fepi41, brekpi41, and direct-lighting to Claude Code (SSH remotes) 
and this Claude.ai project, then clone and run the ai-hedge-fund on fepi41 
for exploration and learning.

---

## Background & Context

Two Raspberry Pi 4 devices are on the Tailscale network: fepi41 runs 
Node-RED for irrigation control, brekpi41 is available for new workloads. 
direct-lighting (iMac 2017) is also on Tailscale and transitional — 
logged for reference before it retires. The goal is to expand Claude's 
reach across all three machines via SSH remotes in Claude Code, document 
their Tailscale addresses, and use fepi41 as the host for the 
virattt/ai-hedge-fund repo for learning and exploration only.

---

## Success Criteria

- [ ] Both Pis added as SSH remotes in Claude Code on MacBook Pro M1
- [x] Tailscale IPs documented for all machines
- [x] Python 3.11.9 installed and confirmed on fepi41
- [x] ai-hedge-fund repo cloned on fepi41
- [x] Dependencies installed
- [x] .env file created with Anthropic API key (no hardcoded keys)
- [x] Successful test run confirmed
- [x] Skills inventory updated in toolkit
- [x] PRD closed and bible entry written

---

## Scope

**In scope:**
- SSH remote setup in Claude Code for both Pis
- Tailscale address documentation for all machines
- ai-hedge-fund clone and setup on fepi41
- API key handling via .env (never hardcoded)
- Exploration/learning use only — no real trades

**Out of scope:**
- Running ai-hedge-fund on brekpi41
- Local LLM inference via Ollama (Pi not sufficient)
- Any live brokerage connection (Schwab or otherwise)
- Modifying Node-RED or irrigation workflows on fepi41
- direct-lighting SSH remote (Tailscale ID logged for reference only)

---

## Machine Inventory

| Machine | Role | Tailscale IP | Username | RAM | Status |
|---|---|---|---|---|---|
| femacbook | Primary | 100.74.137.113 | flint | — | Online |
| fepi41 | Node-RED + hedge fund | 100.72.119.28 | flint | 8GB | Online ✓ |
| brekpi41 | Available | 100.77.133.46 | flint (assumed) | TBD | Offline as of 2026-03-01 |
| direct-lighting | Transitional | 100.110.71.33 | — | — | Online |

> **Note:** direct-lighting rename sweep completed 2026-03-01 across all toolkit files (CLAUDE.md, master-reference.md, skills-inventory.md, README.md, load-context.sh).

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| Tailscale active on all machines | ✓ Confirmed | IPs documented above |
| Claude Code on MacBook Pro M1 | ✓ Complete | |
| SSH enabled on fepi41 | ✓ Confirmed | username: flint |
| SSH enabled on brekpi41 | Unverified | Machine offline |
| Python 3.11.9 on fepi41 | ✓ Confirmed | Via pyenv, global remains 3.13.5 |
| Poetry | Not used | See installation notes below |
| Anthropic API key | ✓ Configured | Via .env only |
| Financial Datasets API key | Not needed | Using free tickers only (AAPL etc.) |

---

## Constraints

- Never store API keys in any file tracked by git
- Do not modify Node-RED or irrigation config on fepi41
- Local LLM (--ollama flag) is out of scope — API only
- No real trades — educational use only
- All pushes to GitHub deliberate (no auto-push)

---

## Plan

### Phase 1 — Connect machines to Claude
- [x] Run Tailscale status on MacBook — confirmed all IPs
- [ ] Add fepi41 as SSH remote in Claude Code ← STILL OPEN
- [ ] Add brekpi41 as SSH remote in Claude Code ← STILL OPEN (offline)
- [x] Document direct-lighting Tailscale IP

### Phase 2 — Verify fepi41 environment
- [x] SSH into fepi41 (flint@100.72.119.28)
- [x] Python 3.13.5 found — too new, installed 3.11.9 via pyenv
- [x] RAM confirmed: 8GB (not 4GB as assumed)
- [x] Disk confirmed: 49GB free

### Phase 3 — Clone and configure ai-hedge-fund
- [x] `git clone https://github.com/virattt/ai-hedge-fund.git`
- [x] `pyenv local 3.11.9` set inside project directory
- [x] Dependencies installed via pip (not Poetry — see lessons)
- [x] `.env` created with Anthropic API key
- [x] `.env` confirmed in `.gitignore`

### Phase 4 — Test run
- [x] Successful run: `python3 -m src.main --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01`
- [x] Growth Analyst returned bearish signal with full reasoning
- [x] Portfolio manager returned HOLD decision
- [x] Michael Burry parsing error noted — known upstream issue, not Pi-related

### Phase 5 — Log and close
- [x] Add ai-hedge-fund entry to skills-inventory.md
- [x] Write bible entry
- [x] Push toolkit updates to GitHub
- [x] Mark PRD complete

---

## Installation Notes (fepi41 — reuse for brekpi41)

**Do not use Poetry on Pi ARM** — virtualenv creation hangs indefinitely.

**Step-by-step install process that worked:**

1. Install pyenv build dependencies first:
```
sudo apt-get install -y libbz2-dev libncurses-dev libffi-dev libreadline-dev libsqlite3-dev liblzma-dev
```

2. Install pyenv, add to ~/.bashrc, reload shell

3. Install Python 3.11.9 via pyenv:
```
pyenv install 3.11.9
pyenv local 3.11.9   ← run inside project directory
```

4. Install Poetry, then generate requirements.txt from poetry.lock using this script:
```python
import toml
lock = toml.load('poetry.lock')
with open('requirements.txt', 'w') as f:
    for pkg in lock['package']:
        if pkg.get('category', 'main') != 'dev':
            f.write(f"{pkg['name']}=={pkg['version']}\n")
```

5. Install additional system deps:
```
sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev rustc cargo
```

6. Exclude packages that won't compile on Pi ARM:
```
grep -v "contourpy\|matplotlib\|pillow\|tiktoken" requirements.txt > requirements-core.txt
python3 -m pip install -r requirements-core.txt
```

**Run command:**
```
python3 -m src.main --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

---

## Open Questions

- [ ] brekpi41 — when will it be powered on?
- [ ] brekpi41 — confirm username is `flint`
- [ ] Claude Code SSH remote setup — still needs to be completed for both Pis

---

## Outcomes & Lessons

- fepi41 is actually 8GB RAM, not 4GB — well-resourced for this workload
- Poetry 2.x removed the `export` command — requires toml workaround to generate requirements.txt
- Poetry install hangs indefinitely on Pi ARM — pip is the reliable path
- Several packages (contourpy, matplotlib, pillow, tiktoken) require native libs that either 
  don't exist on Pi ARM or conflict with GCC 14 — exclude them; they're plotting/tokenizer 
  dependencies not needed for core agent functionality
- pyenv is the correct tool for managing multiple Python versions on Pi, but build deps 
  must be installed via apt BEFORE running pyenv install or the compiled Python will be missing modules
- Tailscale CLI on Mac is not in shell PATH — use full path: 
  /Applications/Tailscale.app/Contents/MacOS/Tailscale status
- Michael Burry agent has a known parsing error in the upstream repo — not a Pi issue

---

## Bible Entry

_Copy to master-reference.md on close._

**Installing Python projects on Raspberry Pi ARM:**
Never use Poetry install directly on Pi ARM — it hangs on virtualenv creation. 
Always install pyenv build deps via apt first, then pyenv, then use pip with a 
generated requirements.txt. Exclude ARM-incompatible packages (contourpy, matplotlib, 
pillow, tiktoken) and pre-install system libs (libjpeg-dev, rustc, cargo etc.) 
before running pip. Poetry 2.x removed the export command — use a toml script 
to generate requirements.txt from poetry.lock instead.

**Tailscale CLI on Mac:**
Not in shell PATH by default. Always use full path:
`/Applications/Tailscale.app/Contents/MacOS/Tailscale status`

---

## Skills Inventory Entry

_Copy to skills-inventory.md on close._

### ai-hedge-fund
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | active |
| Source | https://github.com/virattt/ai-hedge-fund |
| Installed | fepi41: ~/ai-hedge-fund |
| Dependencies | Python 3.11.9 (pyenv), pip, Anthropic API key |
| Purpose | Multi-agent AI trading simulation. Educational/exploration only. Runs analyst agents (Graham, Munger, Burry, etc.) against stock tickers via Anthropic API. No real trades. |
| Risk | External dependency. Calls Anthropic API — costs accrue per run. Monitor usage. |
| Run command | `python3 -m src.main --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01` |
| Notes | Do not use --ollama flag. Do not connect to live brokerage. matplotlib/plotting excluded from install. Michael Burry agent has known upstream parsing error — harmless. |
