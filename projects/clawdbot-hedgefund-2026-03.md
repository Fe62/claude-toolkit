# Clawdbot on fepi41 + Hedge Fund Comms

**Document status:** Active  
**Date started:** 2026-03-03  
**Date completed:**  
**Owner:** Flint  

---

## One-Line Goal

Install Clawdbot on fepi41, wire up Telegram as the first communication
channel, and route ai-hedge-fund agent signals to your phone.

---

## Background & Context

The ai-hedge-fund web UI is already running always-on at
http://100.72.119.28:8000 via systemd (completed 2026-03-03). The next
step is two parallel tracks:

1. **Review nick.nemo's fork** (gitlab.com/nick.nemo/ai-hedgefund) to
   understand what was added or changed vs. the virattt original, and
   decide whether to adopt it.

2. **Install Clawdbot** (github.com/clawdbot/clawdbot) on fepi41 as a
   personal AI assistant accessible via Telegram. Clawdbot runs locally,
   uses your Anthropic Claude Pro/Max subscription or API key, and has a
   built-in Pi agent runtime with native Tailscale support.

First channel: **Telegram** — lowest friction, just a bot token, no
server setup required.

Long-term goal: hedge fund agent run results route to Telegram so
signals arrive on your phone without opening the web UI.

---

## Success Criteria

- [ ] nick.nemo fork reviewed and decision made (adopt / stay on virattt)
- [ ] Node.js upgraded to v22 LTS on fepi41
- [ ] Clawdbot installed and gateway daemon running via systemd
- [ ] Telegram bot token created and channel wired up
- [ ] Can send a message from phone → fepi41 Clawdbot responds
- [ ] At least one hedge fund signal routed to Telegram
- [ ] PRD closed, skills inventory and bible updated

---

## Scope

**In scope:**
- Manual diff of nick.nemo repo vs. virattt original on fepi41
- Node.js upgrade from v20 to v22 LTS on fepi41
- Clawdbot global npm install and onboarding wizard
- systemd daemon install for Clawdbot gateway
- Telegram channel setup (bot token via BotFather)
- Basic hedge fund → Telegram signal routing
- Firewall check for any new ports Clawdbot requires

**Out of scope:**
- Discord (Phase 2 after Telegram is stable)
- WhatsApp, Signal, iMessage (later)
- Exposing Clawdbot to public internet (Tailscale only)
- Modifying Node-RED or irrigation config on fepi41
- Live brokerage connection
- brekpi41 setup

---

## Machine Context

| Machine | Role | Tailscale IP | Node.js | Python |
|---|---|---|---|---|
| femacbook | Primary | 100.74.137.113 | v25.1.0 | — |
| fepi41 | Node-RED + hedge fund + Clawdbot | 100.72.119.28 | v20.19.2 ← needs upgrade | 3.11.9 (pyenv) |

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| fepi41 SSH access | ✓ Confirmed | flint@100.72.119.28 |
| Tailscale active | ✓ Confirmed | Both machines |
| Node.js v22 LTS on fepi41 | ❌ Needs upgrade | Currently v20.19.2; Clawdbot requires ≥22 |
| Anthropic API key | ✓ In .env | Already on fepi41 |
| Telegram account | ✓ Assumed | Need to create bot via BotFather |
| Clawdbot repo | ✓ Public | github.com/clawdbot/clawdbot |

---

## Constraints

- Never store API keys or bot tokens in any tracked file
- Do not modify Node-RED or irrigation config on fepi41
- Clawdbot gateway stays on loopback — Tailscale Serve for remote access
- All GitHub pushes deliberate
- Verify Node upgrade doesn't break ai-hedge-fund.service before proceeding

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Node v20→v22 breaks ai-hedge-fund frontend build | Low | Frontend build is one-time; runtime is Python. Verify service still starts after upgrade. |
| Clawdbot ARM compatibility issues | Medium | 51K stars, active project — ARM issues would be well-documented. Check issues tab before install. |
| Port conflicts with hedge fund service | Low | Clawdbot gateway default is ws://127.0.0.1:18789; hedge fund is port 8000. No conflict. |
| Telegram bot token in config file | Medium | Use environment variable or Clawdbot's secure config path, not a tracked file. |
| Clawdbot consumed too much RAM alongside hedge fund | Low | fepi41 has 8GB RAM — well-resourced for both. Monitor on first run. |

---

## Plan

### Phase 1 — Review nick.nemo fork

- [ ] SSH into fepi41
- [ ] Clone nick.nemo fork into a temp directory:
      `git clone https://gitlab.com/nick.nemo/ai-hedgefund.git ~/nick-hedgefund-review`
- [ ] Run diff against installed virattt version:
      `diff -rq ~/ai-hedge-fund ~/nick-hedgefund-review --exclude='.git' --exclude='*.pyc' --exclude='.env'`
- [ ] Review changed files — focus on: agents, tools, requirements, config
- [ ] Document findings here in Outcomes section
- [ ] Decision: adopt nick.nemo fork / stay on virattt / cherry-pick specific changes

### Phase 2 — Upgrade Node.js to v22 LTS on fepi41

- [ ] SSH into fepi41
- [ ] Check current Node version: `node --version`
- [ ] Download Node v22 LTS ARM64 binary from NodeSource:
      `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -`
      `sudo apt-get install -y nodejs`
- [ ] Confirm upgrade: `node --version` → should return v22.x.x
- [ ] Verify ai-hedge-fund.service still running:
      `sudo systemctl status ai-hedge-fund`
- [ ] Test UI still accessible: curl http://100.72.119.28:8000 from FeMacBook

### Phase 3 — Install Clawdbot

- [ ] Install globally:
      `npm install -g clawdbot@latest`
- [ ] Verify install: `clawdbot --version`
- [ ] Run the onboarding wizard with daemon install:
      `clawdbot onboard --install-daemon`
      The wizard installs the Gateway as a systemd user service.
- [ ] Confirm gateway is running:
      `clawdbot gateway --port 18789 --verbose`
      (Ctrl+C after confirming, daemon handles it from here)
- [ ] Run doctor to check config: `clawdbot doctor`

### Phase 4 — Create Telegram bot and wire channel

- [ ] On phone: open Telegram → search @BotFather → `/newbot`
- [ ] Follow prompts — choose a bot name and username
- [ ] Copy the bot token BotFather provides
- [ ] On fepi41, add token to Clawdbot config (NOT a tracked file):
      Edit `~/.clawdbot/clawdbot.json`:
      ```json
      {
        "agent": {
          "model": "anthropic/claude-opus-4-5"
        },
        "channels": {
          "telegram": {
            "botToken": "YOUR_TOKEN_HERE"
          }
        }
      }
      ```
      Or set via environment variable: `TELEGRAM_BOT_TOKEN=...`
- [ ] Restart Clawdbot gateway: `clawdbot gateway --port 18789`
- [ ] Open Telegram on phone → find your bot → send a message
- [ ] Confirm Clawdbot responds ✓
- [ ] Pair the DM if prompted: `clawdbot pairing approve telegram <code>`

### Phase 5 — Route hedge fund signals to Telegram

- [ ] Run a test hedge fund analysis from fepi41:
      `python3 -m src.main --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01`
- [ ] Identify output format (signals, decisions)
- [ ] Build a small wrapper script that:
      1. Runs the hedge fund analysis
      2. Extracts the signal/decision summary
      3. Sends it via Clawdbot to Telegram:
         `clawdbot message send --to <your-telegram-id> --message "AAPL: HOLD — Growth Analyst bearish"`
- [ ] Test end-to-end: run wrapper → message arrives on phone ✓
- [ ] Save wrapper as a skill in toolkit

### Phase 6 — Validate and close

- [ ] Run `clawdbot doctor` — no warnings
- [ ] Confirm Clawdbot gateway restarts on fepi41 reboot
- [ ] Update skills-inventory.md — add Clawdbot entry
- [ ] Write bible entry — ARM install notes, Telegram config, key gotchas
- [ ] Commit toolkit updates to GitHub
- [ ] Mark PRD complete

---

## Open Questions

- [ ] What did nick.nemo change in his fork? (answer in Phase 1)
- [ ] Does Clawdbot install cleanly on Pi ARM (aarch64)? (answer in Phase 3)
- [ ] Does Clawdbot use a user systemd service (no sudo) or system service? 
      Answer: user service — `clawdbot onboard --install-daemon` handles it.
- [ ] Which Telegram user ID does Clawdbot route to? (answer in Phase 4 pairing step)

---

## Outcomes & Lessons

_To be filled in on completion._

---

## Bible Entry

_To be filled in on completion and copied to master-reference.md._

---

## Skills Inventory Entry

_To be added on close._

### clawdbot
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | pending install |
| Source | https://github.com/clawdbot/clawdbot |
| Installed | fepi41: global npm |
| Dependencies | Node.js v22+, Anthropic API key or Claude Pro/Max |
| Purpose | Personal AI assistant. Connects Claude to Telegram (and others). Gateway runs on fepi41, accessible over Tailscale. Pi agent runtime built in. |
| Config | ~/.clawdbot/clawdbot.json — never commit this file |
| Access | Tailscale only — gateway on loopback + Tailscale Serve |
