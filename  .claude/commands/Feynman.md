# /feynman

Run a Feynman research pass on a topic and save results to the vault.

## Usage
- `/feynman [topic]` — local Ollama, fast and private
- `/feynman deep [topic]` — cloud (Anthropic), full multi-agent

## Steps

1. Parse $ARGUMENTS:
   - If starts with "deep " → MODE=cloud, TOPIC=remainder
   - Otherwise → MODE=local, TOPIC=full argument string

2. Build the command:
   - If MODE=local:
     `feynman deepresearch "$TOPIC"`
   - If MODE=cloud:
     `feynman --model anthropic/claude-opus-4-6 --thinking high deepresearch "$TOPIC"`

3. Set output path:
```bash
   SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
   OUTFILE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/vault/raw/feynman/${SLUG}-$(date +%Y-%m-%d).md"
```

4. Run and save:
```bash
   feynman [command from step 2] > "$OUTFILE"
```

5. Confirm to user:
   - Mode used (local/cloud)
   - Full save path
   - Offer: "Want me to pull key findings into a vault note under `/research/`?"