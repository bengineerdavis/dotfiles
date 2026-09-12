#!/usr/bin/env bash

alias cz='smart_wrap chezmoi help'
alias deliver='clipped p > attachments/emails.txt'
alias kobo='export WINEPREFIX="$HOME/.wine"; wine "$WINEPREFIX/drive_c/Program Files (x86)/Kobo/Kobo Desktop/KoboDesktop.exe" &>/dev/null & disown'

# source: "Could not get lock /var/lib/apt/lists/lock" 
# https://askubuntu.com/a/1545774
alias unlock-apt='sudo service packagekit restart'

# support-based functions
alias pull-attached='fetchurl -i attachments/conversation-*.txt -o attachments'
alias openmail='mailbox "attachments/**" && support-summarized'
alias anonymize='pii-redactor --assume-reviewed -i mail.md -o mail.redacted.md'
alias extract='cat mail.md | triage --model qwen3.6:27b-mlx --platform "Sentry.io" --docs "https://docs.sentry.io" > triage.md'
# top alias
alias investigate='pull-attached && openmail && anonymize && extract && investigate'