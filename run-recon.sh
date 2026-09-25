#!/usr/bin/env bash
#
# run-recon.sh — the whole recon+report flow in one command.
# Run this from the ATTACKER machine (your Kali laptop).
#
#   ./run-recon.sh
#
# It discovers hosts, fingerprints services, saves the scan, and hands it
# to ai_report.py for analysis. Targets come from lab-config.sh.

set -euo pipefail
cd "$(dirname "$0")"
source ./lab-config.sh

OUT="scan_results.txt"

echo ">> Phase 1 — discovery on $LAB_SUBNET"
nmap -sn "$LAB_SUBNET"

echo ">> Phase 2 — service scan of the targets -> $OUT"
# -oN writes 'normal' output, which ai_report.py knows how to read.
nmap -sV -sC -oN "$OUT" $LAB_TARGETS

echo ">> Phase 5 — analysing with the local AI model"
python3 ai_report.py "$OUT"

echo ">> Full scan saved to $OUT"
