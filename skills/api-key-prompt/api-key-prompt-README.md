# api-key-prompt skill

## Purpose
Securely enter API keys in terminal without exposing them in chat, files, or command history.

## Convention (add to CLAUDE.md)
> **API Keys — Never in chat.**
> When any task requires an API key, always instruct the user to run:
> `source ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit/skills/api-key-prompt/set-api-key.sh`
> Never ask for keys in the chat window. Never suggest writing a key into any file.
> Keys set this way are available as environment variables for the current terminal session only.

## Usage
```bash
source ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit/skills/api-key-prompt/set-api-key.sh
```

Note: Use `source` (not `bash` or `./`) so the exported variable is available in your current terminal session.

## How it works
1. Shows a menu of known services
2. You pick one (or type a new service name)
3. Prompts for key with input hidden
4. Exports key as environment variable for the session
5. Key is never written to any file — clears when terminal closes

## Known services (as of 2026-02-24)
- Anthropic → ANTHROPIC_API_KEY
- OpenAI → OPENAI_API_KEY
- Schwab → SCHWAB_API_KEY
- QuickBooks → QUICKBOOKS_API_KEY
- Any new service → auto-generates variable name on the fly

## Adding a new service permanently
Open set-api-key.sh and:
1. Add the service name to the SERVICES array
2. Add its variable name to the ENV_VARS map
