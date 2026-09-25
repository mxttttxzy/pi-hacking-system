# Practice on your Windows laptop today (no Pis needed)

You don't have to wait for the Raspberry Pis. You can run a real vulnerable
target on your own laptop right now and rehearse every attack, then point the
same commands at the Pis later.

## 1. Install Docker Desktop
Download **Docker Desktop for Windows** from docker.com and install it. It uses
WSL2 under the hood; accept the prompt if it offers to set that up.

## 2. Run a practice target
Open PowerShell and start OWASP Juice Shop:

```powershell
docker run -d -p 3000:3000 --name juice bkimminich/juice-shop
```

Open http://localhost:3000 in your browser — that's a full, deliberately
vulnerable web app running on your machine.

Want a second one? DVWA has a difficulty slider (start on "low"):

```powershell
docker run -d -p 8080:80 --name dvwa vulnerables/web-dvwa
```

Then open http://localhost:8080 (login: admin / password).

## 3. Attack it
From Kali (a VM or a second machine), or even from Windows with the tools
installed, point your commands at your own laptop's IP instead of a Pi:

```bash
nmap -sV -sC localhost
# then explore http://localhost:3000 with Burp Suite, sqlmap, etc.
```

Everything you learn here transfers directly — on the real lab you just swap
`localhost` for the Pi's IP (192.168.50.11 and friends).

## 4. Clean up when done
```powershell
docker rm -f juice dvwa
```

## Why this is safe
The containers only listen on your own machine. You are attacking software you
installed, on hardware you own. Same rule as the whole project.
