#!/usr/bin/env bash
# Rebuilds the encrypted MIDAS ENT team protocol pages in team/.
# Usage: TEAM_PASSWORD='...' tools/team_publish.sh <doc.json> <scratch_dir>
#   <doc.json>    Google Docs API read of the MIDAS ENT Protocol (the "content" object)
#   <scratch_dir> a folder OUTSIDE the repo for the readable pages (never commit them)
# Needs staticrypt 3 (npm). The salt in tools/staticrypt.json keeps "Remember me" working
# across rebuilds; changing the password logs everyone out.
set -euo pipefail
[ -n "${TEAM_PASSWORD:-}" ] || { echo "Set TEAM_PASSWORD"; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PLAIN="$2/plain"
rm -rf "$PLAIN"
python3 "$REPO/tools/team_build.py" "$1" "$PLAIN"
rm -rf "$REPO/team"
cd "$REPO"
STATICRYPT_PASSWORD="$TEAM_PASSWORD" npx --yes staticrypt@3 "$PLAIN"/*.html -d team -c tools/staticrypt.json \
  --short --remember 90 \
  -t tools/team_template.html \
  --template-title "MIDAS ENT Protocols" \
  --template-instructions "MIDAS ENT team only. Enter the team password." \
  --template-button "Open" --template-placeholder "Team password" \
  --template-remember "Remember me on this phone" \
  --template-error "Wrong password" \
  --template-color-primary "#13493b" --template-color-secondary "#eef3f1"
echo "Encrypted $(ls "$REPO/team" | wc -l) pages into team/"
