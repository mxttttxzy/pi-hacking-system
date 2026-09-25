#!/usr/bin/env bash
#
# setup-ai-node.sh — prepare Pi #4 (the AI HAT+ node).
# Run this ON the AI Pi once it's plugged in and still has internet
# (it needs to download the model once; after that it runs offline).
#
#   sudo ./setup-ai-node.sh
#
# Installs Ollama and a small local model so ai_report.py can analyse
# scans entirely on-device. The Hailo AI HAT+ best accelerates vision /
# detection work; the text model here stays small on purpose.

set -euo pipefail
cd "$(dirname "$0")"
source ./lab-config.sh

if [[ $EUID -ne 0 ]]; then echo "Please run with sudo."; exit 1; fi

echo ">> Setting the AI node's static IP to $IP_AI"
if command -v nmcli >/dev/null 2>&1; then
  CON="$(nmcli -t -f NAME connection show --active | head -n1)"
  if [[ -n "$CON" ]]; then
    nmcli connection modify "$CON" \
      ipv4.method manual ipv4.addresses "$IP_AI/$LAB_PREFIX" ipv4.gateway "" ipv4.dns ""
  else
    echo "!! No active NetworkManager connection found. Set the IP manually to $IP_AI/$LAB_PREFIX."
  fi
else
  echo "!! nmcli not found; set the IP manually to $IP_AI/$LAB_PREFIX, then continue."
fi

echo ">> Installing Ollama (needs internet for this step)..."
curl -fsSL https://ollama.com/install.sh | sh

echo ">> Pulling a small model for on-device analysis..."
# 1B model keeps memory and heat in check on a Pi. Swap for a bigger one later.
ollama pull llama3.2:1b

echo ">> Optional: install the Hailo AI HAT+ software stack"
echo "   Follow Raspberry Pi's official guide, then use the HAT for the"
echo "   traffic-analysis / anomaly-detection demo (the blue-team piece)."

echo ""
echo ">> Test it now:"
echo "   python3 ai_report.py sample_scan.txt"
echo ">> Once this Pi is on the lab network, it runs with no internet at all."
