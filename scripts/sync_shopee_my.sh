#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
umask 077
exec python3 app/shopee_sync.py --date "${SYNC_DATE:-$(date -u +%F)}" --days "${SYNC_DAYS:-15}"
