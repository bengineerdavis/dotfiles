#!/usr/bin/env bash


# bash strict mode
set -euo pipefail
IFS=$'\n\t'

# Uncomment line below to enable full line-by-line debugging
# set -x

# The cron job you want to add
CRON_JOB=$1

# Check if the cron job already exists
crontab -l > current_crontab
if ! grep -Fxq "$CRON_JOB" current_crontab; then
    # Add the cron job if it doesn't exist
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully."
else
    echo "Cron job already exists."
fi

# Clean up
rm current_crontab