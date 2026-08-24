#!/usr/bin/env bash

alias cz='smart_wrap chezmoi help'
alias deliver='clipped p > attachments/emails.txt'
alias kobo='export WINEPREFIX="$HOME/.wine"; wine "$WINEPREFIX/drive_c/Program Files (x86)/Kobo/Kobo Desktop/KoboDesktop.exe" &>/dev/null & disown'

# source: "Could not get lock /var/lib/apt/lists/lock" 
# https://askubuntu.com/a/1545774
alias unlock-apt='sudo service packagekit restart'
