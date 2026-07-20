#!/usr/bin/env bash

topic="$1"

# ansible is mise-managed; `mise exec` guarantees it's on PATH.
if [ "$#" -ge 2 ] && [ -n "${2:-}" ]; then
	mise exec -- ansible-playbook -vv -i localhost run-role.yaml -e "topic=$topic" --tags "$2"
else
	mise exec -- ansible-playbook -vv -i localhost run-role.yaml -e "topic=$topic"
fi