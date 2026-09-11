#!/usr/bin/env bash
# Deliberately wrong: unquoted expansion inside a test.
x="a b"
if [ "$x" = 1 ]; then
  echo yes
fi
