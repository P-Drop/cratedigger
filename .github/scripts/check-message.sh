#!/usr/bin/env bash
# Rules for any message that reaches main: commit messages and the PR title.
# Usage: check-message.sh <message-file> <label>
set -uo pipefail

file="$1"
label="$2"
subject="$(head -n 1 "$file")"
status=0

# Format and types come from the hook in .pre-commit-config.yaml.
if ! uv run pre-commit run conventional-pre-commit \
    --hook-stage commit-msg --commit-msg-filename "$file"; then
  echo "::error::Not conventional: $label"
  status=1
fi

# The hook accepts these prefixes unless --strict, which would also apply locally.
case "${subject,,}" in
  "amend! "* | "fixup! "* | "squash! "*)
    echo "::error::Autosquash or merge message: $label"
    status=1
    ;;
esac

if [ "${#subject}" -gt 72 ]; then
  echo "::error::Subject over 72 chars (${#subject}): $label"
  status=1
fi

exit "$status"
