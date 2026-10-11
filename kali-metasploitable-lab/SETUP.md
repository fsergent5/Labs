# Setup Guide (Steps 1–3)

This walks through building the lab. The guiding principle is **isolation**: both
VMs sit on a **host-only** network so traffic stays between the two VMs and your
host, never reaching the internet.

---

## Step 1 — Install a hypervisor

Pick one. All are free for this use.

| Host OS | Recommended | Notes |
|---------|-------------|-------|
| Windows | VMware Workstation Pro (now free from Broadcom) or VirtualBox | Download Workstation Pro with your school email from the Broadcom portal |
| Linux   | VMware Workstation Pro or VirtualBox | — |
| macOS (Apple Silicon) | **UTM** | VMware/VirtualBox x86 images don't run well on ARM; UTM is the practical choice |
| macOS (Intel) | VMware Fusion or VirtualBox | — |

**BIOS/UEFI hint:** if VMs won't start or run 64-bit guests, enable CPU
virtualization in firmware — **Intel VT-x** or **AMD-V** (sometimes labeled
"SVM Mode" or "Virtualization Technology"). On Windows, also disabling
Hyper-V / "Memory Integrity" sometimes resolves conflicts with VMware/VirtualBox.

**32- vs 64-bit:** virtually all modern machines are 64-bit. Confirm:
- Windows: Settings → System → About → *System type*.
- Linux/macOS: run `uname -m` (`x86_64`/`arm64` = 64-bit).

Download the **64-bit** images unless you've confirmed a 32-bit host.

---

## Step 2 — Install Kali Linux (the attacker)

1. Go to the official site: **https://www.kali.org/get-kali/** → *Virtual Machines*.
2. Download the **pre-built** image matching your hypervisor (VMware `.7z`/`.zip`,
   VirtualBox `.7z`, or build a UTM image on Apple Silicon).
3. Extract the archive. For VMware, open the extracted `.vmx` (the folder also
   contains the `.vmdk` virtual disk). For VirtualBox, import the `.ova`/`.vbox`.
4. **Set the network adapter to Host-only** *before* first boot:
   - **VMware:** VM → Settings → Network Adapter → **Host-only**.
   - **VirtualBox:** Settings → Network → Adapter 1 → Attached to **Host-only Adapter**.
5. Boot and log in. Modern Kali images use **`kali` / `kali`**. Older images used
   **`root` / `toor`**. If you need root: `sudo -i` (then your user password).

You now have a working Kali install on a host-only network.

### Verify Kali's network
```bash
ip a                 # note Kali's host-only IP, e.g. 192.168.56.101
```

---

## Step 3 — Install Metasploitable 2 (the target) and reach DVWA

Metasploitable 2 ships as a pre-built virtual disk — you **attach** it, you don't
install an OS.

1. Download **Metasploitable 2** (Rapid7 / SourceForge:
   `https://sourceforge.net/projects/metasploitable/`). Extract the zip; you'll get
   a folder with `Metasploitable.vmdk` and its child files.
2. Create the VM shell:
   - **VMware:** File → New Virtual Machine → **Custom** → *I will install the
     operating system later* → Guest OS **Linux / Ubuntu (64-bit)** → set CPU/RAM
     (1 CPU, 512 MB–1 GB is plenty) → **Network: Host-only** → **Use an existing
     virtual disk** → browse to `Metasploitable.vmdk` → Finish.
     - Keep all child `.vmdk` files in the same folder as the one you select.
   - **VirtualBox:** New → Type Linux / Ubuntu 64-bit → *Use an existing virtual
     hard disk file* → `Metasploitable.vmdk` → after creating, Settings → Network →
     **Host-only Adapter**.
3. **Crash fix (VMware):** if Metasploitable keeps crashing, open VM Settings →
   Display → **turn off "Accelerate 3D graphics" (3D video support)**.
4. Boot it and log in at the console:
   ```
   Username: msfadmin
   Password: msfadmin
   ```
5. Get the target's IP:
   ```bash
   ifconfig          # look under eth0 -> inet addr, e.g. 192.168.56.102
   ```
   (`ip a` also works.)

### Reach DVWA from Kali

Metasploitable 2 ships with **DVWA** (Damn Vulnerable Web Application). From the
**Kali** VM, open **Firefox** and browse to the target's IP:

```
http://<METASPLOITABLE_IP>/dvwa/
```

e.g. `http://192.168.56.102/dvwa/`

**Default DVWA credentials:**

```
Username: admin
Password: password
```

Log in. After a successful login, **take a screenshot** and save it as:

```
screenshots/step3-dvwa-login.png
```

> This screenshot is required by Step 4 and must be captured on your own machine
> with both VMs running — it can't be generated from code. `REPORT.md` references
> that filename, so once you drop the image in `screenshots/` the report is complete.

### Sanity check: can the two VMs see each other?
From Kali:
```bash
ping -c 3 <METASPLOITABLE_IP>
```
If ping succeeds, the host-only network is wired correctly and you're ready for
Step 4.
