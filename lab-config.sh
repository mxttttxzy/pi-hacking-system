#!/usr/bin/env bash
# Shared settings for the lab. Every other script reads this file.
# Edit the IPs here if your network uses a different range.

export LAB_SUBNET="192.168.50.0/24"
export LAB_PREFIX="24"

# Static IPs for each device (must match your addressing plan).
export IP_LAPTOP="192.168.50.10"   # attacker
export IP_PI1="192.168.50.11"      # web target
export IP_PI2="192.168.50.12"      # service target
export IP_PI3="192.168.50.13"      # network target
export IP_AI="192.168.50.20"       # AI HAT+ node

# All the targets, for scanning in one go.
export LAB_TARGETS="$IP_PI1 $IP_PI2 $IP_PI3"
