#!/usr/bin/env bash

set -e

DISPOSITIVO="${1:-/dev/ihs_projeto}"
FRAMES="${2:-2}"
LIMIAR_ABAIXAR="${3:-125}"
LIMIAR_LEVANTAR="${4:-160}"

sudo venv/bin/python3 adaptadores/webcam/webcam_mamip.py \
  --enviar \
  --dispositivo "$DISPOSITIVO" \
  --ignorar-polegar \
  --frames-estaveis "$FRAMES" \
  --limiar-abaixar "$LIMIAR_ABAIXAR" \
  --limiar-levantar "$LIMIAR_LEVANTAR"