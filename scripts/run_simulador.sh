#!/usr/bin/env bash

set -e

DISPOSITIVO="${1:-/tmp/ihs_projeto_simulado}"

python3 simulador/simulador_manual.py --dispositivo "$DISPOSITIVO"