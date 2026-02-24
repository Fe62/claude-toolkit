#!/bin/zsh

# set-api-key.sh
# Prompts for an API key securely in terminal and exports it to the current session.
# Key is never written to any file — lives in memory only for this session.

echo ""
echo "=== API Key Prompt ==="
echo ""
echo "Select a service:"
echo ""
echo "  1. Anthropic"
echo "  2. OpenAI"
echo "  3. Schwab"
echo "  4. QuickBooks"
echo "  5. Other (enter manually)"
echo ""
read "CHOICE?Choice: "

case $CHOICE in
  1) SERVICE="Anthropic";  VAR_NAME="ANTHROPIC_API_KEY" ;;
  2) SERVICE="OpenAI";     VAR_NAME="OPENAI_API_KEY" ;;
  3) SERVICE="Schwab";     VAR_NAME="SCHWAB_API_KEY" ;;
  4) SERVICE="QuickBooks"; VAR_NAME="QUICKBOOKS_API_KEY" ;;
  5)
    echo ""
    read "SERVICE?Service name (e.g. Stripe): "
    VAR_NAME=$(echo "${SERVICE}_API_KEY" | tr '[:lower:]' '[:upper:]' | tr ' ' '_')
    ;;
  *)
    echo "Invalid choice. Exiting."
    return 1
    ;;
esac

echo ""
echo "Entering key for: $SERVICE"
echo "Variable name:    $VAR_NAME"
echo ""
read -s "API_KEY?Paste your API key (input hidden): "
echo ""

if [[ -z "$API_KEY" ]]; then
  echo "No key entered. Exiting."
  return 1
fi

export "$VAR_NAME"="$API_KEY"

echo ""
echo "✓ $VAR_NAME set for this terminal session."
echo "  Key will be cleared when this terminal window closes."
echo ""
