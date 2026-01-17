#!/bin/bash
set -e

MANIFEST="security_manifests/V2_INTEGRITY_MANIFEST.sha256"

echo "[VERIFY] Checking V2 integrity..."
sha256sum -c "$MANIFEST"
echo "[VERIFY] V2 integrity VERIFIED"
