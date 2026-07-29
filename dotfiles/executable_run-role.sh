#!/usr/bin/env bash
set -euo pipefail

# Run a single topic's standalone role playbook.
# Usage: run-role.sh <topic> [tag]
#   run-role.sh docker install     # install just the docker topic
#   run-role.sh docker             # provision just the docker topic (no remove)
#   run-role.sh docker remove      # uninstall (remove is opt-in; tagged `never`)
#
# Each topic is a standalone play at apps/<topic>/playbook.yaml (roles layout).
# We invoke it directly so --tags routes to the role's lifecycle tasks. The
# old run-role.yaml include-wrapper predates the roles migration and no longer
# works (a topic playbook is a play, not a task file).
#
# `-i localhost,` (trailing comma) is an inline host list, not an inventory
# file. ansible is mise-managed; `mise exec` guarantees it's on PATH.

topic="$1"
playbook="apps/${topic}/playbook.yaml"

if [ ! -f "$playbook" ]; then
	echo "run-role.sh: no such topic playbook: $playbook" >&2
	exit 1
fi

if [ "$#" -ge 2 ] && [ -n "${2:-}" ]; then
	mise exec -- ansible-playbook -vv -i localhost, "$playbook" --tags "$2"
else
	mise exec -- ansible-playbook -vv -i localhost, "$playbook"
fi
