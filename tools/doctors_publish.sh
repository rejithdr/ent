#!/usr/bin/env bash
# Rebuilds the encrypted MERA ENT Pathways page in doctors/ (doctors-only, separate password from team/).
# Usage: DOCTORS_PASSWORD='...' tools/doctors_publish.sh <artifact files folder> <scratch_dir>
# Remember-me uses its own storage keys (tools/doctors_template.html) so it never clashes with the team login.
set -euo pipefail
[ -n "${DOCTORS_PASSWORD:-}" ] || { echo "Set DOCTORS_PASSWORD"; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$2/plain"; python3 "$REPO/tools/doctors_build.py" "$1" "$2/plain/index.html"
cd "$REPO"; rm -rf doctors
STATICRYPT_PASSWORD="$DOCTORS_PASSWORD" npx --yes staticrypt@3 "$2/plain/index.html" -d doctors -c tools/staticrypt_doctors.json \
  --short --remember 90 -t tools/doctors_template.html \
  --template-title "MERA ENT Pathways" \
  --template-instructions "For doctors invited by Dr Rejith R S. Enter the doctors' password." \
  --template-button "Open" --template-placeholder "Doctors' password" \
  --template-remember "Remember me on this phone" --template-error "Wrong password" \
  --template-color-primary "#1f6f6a" --template-color-secondary "#eef3f1"
echo "Encrypted into doctors/"
