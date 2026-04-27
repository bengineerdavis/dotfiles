#!/usr/bin/env bash

topic="$1"

if [ "$#" -ge 2 ] && [ -n "${2:-}" ]; then
	ansible-playbook -vv -i localhost run-role.yaml -e "topic=$topic" --tags "$2"
else
	ansible-playbook -vv -i localhost run-role.yaml -e "topic=$topic"
fi