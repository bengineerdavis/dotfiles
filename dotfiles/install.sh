#!/usr/bin/env bash

ansible-playbook -v -i localhost playbook.yaml --tags "install"