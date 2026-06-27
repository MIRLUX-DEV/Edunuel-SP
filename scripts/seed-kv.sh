#!/usr/bin/env bash
# Carga el horóscopo inicial en KV (solo la primera vez o para resetear).
set -euo pipefail
cd "$(dirname "$0")/.."
wrangler kv key put horoscope --namespace-id=5dea61df36b641f199aada56db691ca5 --path=data/horoscopo.json
