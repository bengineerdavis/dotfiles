#!/usr/bin/env bash

# ansible is a mise-managed tool (pipx:ansible, built with the system uvx).
# `mise exec` guarantees it's on PATH even if this shell hasn't activated mise.
# ansible-playbook -v -i localhost playbook.yaml --tags "install"
mise exec -- ansible-playbook -v -i localhost playbook.yaml