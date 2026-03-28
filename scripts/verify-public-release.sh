#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "==> Frontend lint"
(cd frontend && corepack yarn lint)

echo "==> Frontend build"
(cd frontend && corepack yarn build)

echo "==> Backend tests"
conda run -n daily-brief python -m pytest backend/tests -q

echo "==> Public-safety scan"
if rg -n "Lumiad|Cult|Aravind|Ashwin|mock-jwt-token|component-forge|Briefly|Demo: Any email|Track your team|Sarah|Alex|sse/aravind|gmail\\.com" README.md .gitignore backend frontend docs/public; then
  echo
  echo "Public-safety scan failed."
  exit 1
fi

echo
echo "Public release verification passed."
