#!/usr/bin/env bash

set -e

sudo rmmod ihs_projeto 2>/dev/null || true

echo "Driver removido."