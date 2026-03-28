# fepi41 — Irrigation System State
**Last updated:** 2026-03-27

---

## Node-RED Access

| | |
|---|---|
| URL (remote) | http://100.72.119.28:1880 |
| URL (local on fepi41) | http://localhost:1880 |
| Username | `Fl1nte` |
| Password | `778787` |
| Flow file | `/home/flint/.node-red/Flint.flows` |

**Get Bearer token:**
```bash
curl -s -X POST http://localhost:1880/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"node-red-admin","grant_type":"password","scope":"*","username":"Fl1nte","password":"778787"}'
```

**Deploy full flow:**
```bash
curl -s -X POST http://localhost:1880/flows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Node-RED-Deployment-Type: full" \
  -d @/tmp/patched_flows.json
```

---

## Key Node IDs

| ID | Name |
|---|---|
| `scheduler` | Irrigation Scheduler (global) |
| `sched-inject-daily` | Run scheduler (06:00 daily) |
| `366c8803210a432b` | irrigation MQTT |
| `fa34d41e21286d94` | hour check |
| `ack-watch-inject` | ACK watchdog (30s) |
| `valve-cmd-register` | Register pending valve ack |
| `heat-cycle-sched` | Heat Cycle Scheduler |
| `d14d419ee254e9b4` | water journalling |

---

## What's Live

- ✅ **Water journalling** — global context fix (`wj_selected_relay_id`, `wj_relay_start_time`); output wired to `water log entry` link → `wj-email-fmt` → email node
- ✅ **Valve ACK loop** — `Register pending valve ack` intercepts all downlinks; `Valve ACK checker` (30s) confirms or retries; alert email on 2nd failure
- ✅ **Secondary irrigation cycle** — 30 min after primary finishes, re-runs only zones still reading under 15% moisture at runtime. Duration adapts to however many zones actually run.
- ✅ **Heat cycle** — `Heat Cycle Scheduler` wired off `hour check`:
  - **Noon:** all valves 5 min if any node temp > 100°F (once/day)
  - **Evening (6 PM):** all valves normal duration if any node temp > 95°F (once/day)
  - Ignores alternating-day schedule
  - De-dupe keys: `heat_noon_fired_YYYY-MM-DD` / `heat_evening_fired_YYYY-MM-DD`

---

## Still Needs Testing

- [ ] **ACK retry/alert path** — needs an offline TTN device; send a downlink, wait 6+ min to observe retry then alert email
- [ ] **Secondary cycle** — temporarily lower `SECOND_CYCLE_THRESH` to 80% to force trigger on next run
- [ ] **Heat cycle** — temporarily lower temp thresholds to current ambient to force trigger
- [ ] **Tomorrow's 06:00 run** — will exercise primary + secondary cycle + water journalling email end-to-end

---

## Hardware

| Node | Valves | Fports | Schedule |
|---|---|---|---|
| `relay-node1` | ss1–ss4 | 6–9 | Mon/Wed/Fri (dow 0,2,4) |
| `relay-node-2` | ss5–ss8 | 6–9 | Tue/Thu/Sat (dow 1,3,5) |

- TTN app: `5571-258-irri@ttn`
- MQTT broker: `nam1.cloud.thethings.network:8883` (TLS)
- Google app password for NR email node: `pqft eewj ayzh zoxk`

---

## Testing Tips

- To test hour-triggered email nodes without waiting for the scheduled hour: edit the node's JSON in the flow, set the trigger hour to the current hour, redeploy. Revert after.
- To pull current flow JSON:
  ```bash
  curl -s http://localhost:1880/flows -H "Authorization: Bearer $TOKEN" > /tmp/current_flows.json
  ```
