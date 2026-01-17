#!/bin/bash
set -e

MANIFEST="security_manifests/V2_INTEGRITY_MANIFEST.sha256"

echo "[LOCK] Generating integrity manifest..."

find v2_model \
  -type f \
  ! -path "v2_model/plots/*" \
  ! -path "v2_model/logs/*" \
  ! -name "*.png" \
  -exec sha256sum {} \; | sort > "$MANIFEST"

chmod 400 "$MANIFEST"
echo "[LOCK] Manifest written to $MANIFEST"
