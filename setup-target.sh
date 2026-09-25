#!/usr/bin/env bash
#
# setup-target.sh — prepare ONE target Raspberry Pi for the lab.
# Run this ON the Pi (over SSH or with a keyboard) once it's plugged in.
#
#   sudo ./setup-target.sh web        # Pi #1  -> Juice Shop + DVWA
#   sudo ./setup-target.sh service    # Pi #2  -> weak SSH + FTP
#   sudo ./setup-target.sh network    # Pi #3  -> web + Samba share
#
# What it does:
#   1. Sets the Pi's static lab IP (no internet gateway).
#   2. Installs Docker.
#   3. Runs the deliberately-vulnerable target software for that role.
#
# EVERYTHING here is intentionally weak. Only ever run it on a Pi you own,
# on your isolated lab network. Never on a machine that touches the internet.

set -euo pipefail
cd "$(dirname "$0")"
source ./lab-config.sh

ROLE="${1:-}"
case "$ROLE" in
  web)     IP="$IP_PI1" ;;
  service) IP="$IP_PI2" ;;
  network) IP="$IP_PI3" ;;
  *) echo "Usage: sudo $0 {web|service|network}"; exit 1 ;;
esac

if [[ $EUID -ne 0 ]]; then echo "Please run with sudo."; exit 1; fi

echo ">> Configuring Pi #[$ROLE] with static IP $IP"

# --- 1. Static IP via NetworkManager (Raspberry Pi OS Bookworm and newer) ---
# Leaves the gateway blank on purpose, so the Pi has no route to the internet.
CON="$(nmcli -t -f NAME connection show --active | head -n1)"
if [[ -n "$CON" ]]; then
  nmcli connection modify "$CON" \
    ipv4.method manual \
    ipv4.addresses "$IP/$LAB_PREFIX" \
    ipv4.gateway "" \
    ipv4.dns ""
  echo ">> Static IP set on connection '$CON'. It applies on next network restart."
else
  echo "!! No active NetworkManager connection found. Set the IP manually to $IP/$LAB_PREFIX."
fi

# --- 2. Docker (pull images while the Pi still has internet, THEN isolate) ---
if ! command -v docker >/dev/null 2>&1; then
  echo ">> Installing Docker... (needs internet for this step)"
  curl -sSL https://get.docker.com | sh
  usermod -aG docker "${SUDO_USER:-pi}" || true
fi

# --- 3. Role-specific vulnerable software ---
echo ">> Deploying the '$ROLE' target software..."
case "$ROLE" in
  web)
    docker rm -f juice dvwa 2>/dev/null || true
    docker run -d --restart unless-stopped --name juice -p 3000:3000 bkimminich/juice-shop
    docker run -d --restart unless-stopped --name dvwa  -p 80:80   vulnerables/web-dvwa
    echo ">> Juice Shop on :3000, DVWA on :80"
    ;;
  service)
    # Deliberately weak SSH: restore the default account + password for practice.
    echo "pi:raspberry" | chpasswd
    systemctl enable --now ssh
    # Anonymous, plaintext FTP for practice.
    apt-get update && apt-get install -y vsftpd
    sed -i 's/^#*anonymous_enable=.*/anonymous_enable=YES/' /etc/vsftpd.conf
    systemctl enable --now vsftpd
    echo ">> Weak SSH (pi/raspberry) + anonymous FTP enabled"
    ;;
  network)
    docker rm -f web smb 2>/dev/null || true
    docker run -d --restart unless-stopped --name web -p 80:80 httpd:2.4
    docker run -d --restart unless-stopped --name smb -p 445:445 \
      dperson/samba -s "public;/share;yes;no;yes" -p
    echo ">> Apache on :80, open Samba share on :445"
    ;;
esac

echo ""
echo ">> Done. Unplug this Pi from the internet and move it to the lab switch."
echo ">> Verify from the laptop:  nmap -sV $IP"
