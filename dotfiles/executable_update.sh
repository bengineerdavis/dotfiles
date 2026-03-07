#!/usr/bin/env bash

ansible-playbook -vv -i localhost playbook.yaml --tags "upgrade"