#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -q 'gh pr create'; then
  sleep 2
  gh pr checks --watch

elif echo "$COMMAND" | grep -qE '^git push'; then
  sleep 3
  gh run watch

elif echo "$COMMAND" | grep -q 'gh issue create'; then
  sleep 2
  gh run watch
fi
