#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/pages/dist"

if [[ ! -f "$DIST/index.html" ]]; then
  echo "pages/dist/index.html not found. Run: cd pages/vue-app && npm ci && npm run build" >&2
  exit 1
fi

rm -rf "$ROOT/assets"
cp -a "$DIST/assets" "$ROOT/assets"
cp -a "$DIST/index.html" "$ROOT/index.html"
cp -a "$DIST/google7ac8e510bcec8842.html" "$ROOT/google7ac8e510bcec8842.html"
touch "$ROOT/.nojekyll"

echo "Synced pages/dist to repository root for GitHub Pages."
