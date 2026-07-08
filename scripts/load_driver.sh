#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/../driver"

make clean
make

sudo rmmod ihs_projeto 2>/dev/null || true
sudo insmod ./ihs_projeto.ko

echo "Driver carregado."
ls -l /dev/ihs_projeto