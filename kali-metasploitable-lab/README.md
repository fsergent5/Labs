# Kali Linux + Metasploitable 2 Penetration Testing Lab

A virtual penetration-testing lab for coursework. An attacker VM (**Kali Linux**)
and an intentionally vulnerable target VM (**Metasploitable 2**) are placed on an
**isolated host-only network** so that all testing stays inside the lab and never
touches the real network or the internet.

> **Scope and ethics.** Metasploitable 2 and DVWA are *built to be attacked* for
> training. Everything here is performed against your own VMs on a host-only
> network. Running these techniques against any system you do not own or lack
> written permission to test is illegal. Keep the lab offline (host-only).

## Contents

| File | Purpose |
|------|---------|
| `SETUP.md`   | Steps 1–3: install VMware/VirtualBox, Kali, and Metasploitable 2; network config; DVWA login |
| `REPORT.md`  | Step 4: attack research and demonstrations against Metasploitable 2 |
| `screenshots/` | Place your Step 3 DVWA login screenshot and any attack screenshots here |

## Quick reference

```
Attacker (Kali)          Target (Metasploitable 2)
---------------          -------------------------
login: kali / kali       login: msfadmin / msfadmin
(or root / toor on       DVWA:  admin / password
 older images)           host-only network only
```

Start here: **`SETUP.md`**, then **`REPORT.md`**.
