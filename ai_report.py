#!/usr/bin/env python3
"""
ai_report.py — turn an nmap scan into a findings report.

This is the "AI HAT+" brain of the lab. It:
  1. Parses an nmap output file (open ports + service versions).
  2. Sends the findings to a LOCAL model (Ollama on localhost) if one is
     running — nothing leaves the machine, no internet needed.
  3. Falls back to a built-in rule set if no local model is available,
     so it still works on your laptop today, before the AI HAT+ arrives.

Usage:
    python3 ai_report.py sample_scan.txt
    python3 ai_report.py sample_scan.txt --model llama3.2:1b
    python3 ai_report.py sample_scan.txt --no-ai      # rules only

Only standard library is used, so it runs anywhere Python 3 does.
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"

# Known service -> (why it matters, how to fix it). Used for the offline
# fallback and to give the local model solid hints.
KNOWN = {
    "ssh":    ("Remote login. Weak or default passwords let attackers straight in.",
               "Disable password login, use SSH keys, and never keep the default 'pi/raspberry' account."),
    "ftp":    ("File transfer, often anonymous or plaintext. Credentials travel unencrypted.",
               "Replace FTP with SFTP/SCP, or disable it. Never allow anonymous write."),
    "telnet": ("Plaintext remote shell. Everything, including the password, is sent in the clear.",
               "Disable Telnet entirely and use SSH instead."),
    "http":   ("A web app. Common home of SQL injection, XSS, and broken authentication.",
               "Patch the app, validate all input, and put it behind HTTPS."),
    "https":  ("Encrypted web app. Still vulnerable at the application layer.",
               "Keep the app patched and test it for injection and auth flaws."),
    "smb":    ("Windows file sharing. Frequently exposes shares with weak permissions.",
               "Restrict shares, require authentication, and keep SMB off the internet."),
    "microsoft-ds": ("SMB file sharing (port 445). A classic lateral-movement target.",
                     "Restrict shares and require authentication."),
    "mysql":  ("A database. Direct exposure risks a full data dump.",
               "Bind the database to localhost and require strong credentials."),
}


def parse_nmap(text):
    """Pull (port, proto, service, version) rows out of nmap normal output."""
    services = []
    host = None
    for line in text.splitlines():
        line = line.strip()
        m_host = re.search(r"Nmap scan report for (\S+)", line)
        if m_host:
            host = m_host.group(1)
        # e.g. "3000/tcp open  http    Node.js Express framework"
        m = re.match(r"(\d+)/(tcp|udp)\s+open\s+(\S+)\s*(.*)", line)
        if m:
            port, proto, service, version = m.groups()
            services.append({
                "host": host,
                "port": int(port),
                "proto": proto,
                "service": service.lower(),
                "version": version.strip(),
            })
    return services


def rule_findings(services):
    """Offline fallback: map each open service to a finding and a fix."""
    findings = []
    for s in services:
        why, fix = KNOWN.get(s["service"], (
            "An exposed service. Anything listening on the network is worth reviewing.",
            "Confirm it's needed; if not, turn it off. Keep it patched if it stays.",
        ))
        sev = "HIGH" if s["service"] in ("telnet", "ftp") else \
              "MEDIUM" if s["service"] in ("ssh", "smb", "microsoft-ds", "mysql") else "REVIEW"
        findings.append({
            "target": f"{s['host'] or '?'}:{s['port']}",
            "service": f"{s['service']} {s['version']}".strip(),
            "severity": sev,
            "why": why,
            "fix": fix,
        })
    return findings


def ask_local_model(services, model):
    """Send the findings to a local Ollama model. Returns text, or None."""
    summary = "\n".join(
        f"- {s['host']}:{s['port']} {s['service']} {s['version']}".rstrip()
        for s in services
    )
    prompt = (
        "You are a security tutor helping a student with their OWN isolated "
        "practice lab. These open services were found on lab machines the "
        "student owns. For each one, give a one-line risk and a one-line fix, "
        "in plain language a beginner understands.\n\n"
        f"Open services:\n{summary}\n\nReport:"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response", "").strip() or None
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return None


def print_report(services, ai_text, findings):
    line = "=" * 60
    print(line)
    print("  RASPBERRY PI SECURITY LAB — FINDINGS REPORT")
    print(line)
    print(f"\nOpen services found: {len(services)}\n")
    for s in services:
        print(f"  {s['host'] or '?':<15} :{s['port']:<6} {s['service']} {s['version']}".rstrip())

    if ai_text:
        print("\n" + line)
        print("  AI ANALYSIS (local model, on-device)")
        print(line + "\n")
        print(ai_text)
    else:
        print("\n" + line)
        print("  ANALYSIS (built-in rules — no local model running)")
        print(line + "\n")
        for f in findings:
            print(f"[{f['severity']}] {f['target']}  ({f['service']})")
            print(f"    Risk: {f['why']}")
            print(f"    Fix : {f['fix']}\n")

    print(line)
    print("  Reminder: only run this against machines you own, in your lab.")
    print(line)


def main():
    ap = argparse.ArgumentParser(description="Turn an nmap scan into a findings report.")
    ap.add_argument("scan_file", help="Path to an nmap output text file")
    ap.add_argument("--model", default="llama3.2:1b", help="Local Ollama model name")
    ap.add_argument("--no-ai", action="store_true", help="Skip the local model, use rules only")
    args = ap.parse_args()

    try:
        with open(args.scan_file, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as e:
        print(f"Could not read {args.scan_file}: {e}", file=sys.stderr)
        return 1

    services = parse_nmap(text)
    if not services:
        print("No open services found in that scan file. "
              "Is it nmap 'normal' output (nmap -oN)?", file=sys.stderr)
        return 1

    findings = rule_findings(services)
    ai_text = None
    if not args.no_ai:
        ai_text = ask_local_model(services, args.model)

    print_report(services, ai_text, findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
