---
title: "MonitorsFour"
machine: MonitorsFour
tags: HackTheBox Machines
---
#### Write-Up for the HackTheBox Machine - MonitorsFour
<!--more-->
---
#### 001: Scan

The victim machine was scanned using `nmap`.
Ports returned from the tool were `port 80(http)` and `port 5985 (winrm)`.

```bash
nmap -sC -sV -p- 10.10.11.98
```

{{< screenshots "shot-001" >}}

---
#### 002: Hostname Mapping

Then, the IP of the victim is added to `/etc/hosts` and mapped to `monitorsfour.htb` for local hostanme resolution.
Thus, the website was viewed in browser for further examination.

{{< screenshots "shot-002" >}}

---
#### 003: Victim Fuzz

As the `nmap` report showed that the application was running on nginx, additional reconnaissance for the discovery of hidden files and subdomains was made using `ffuf`.
`common.txt` wordlist exposed various paths, but what seemed most interesting was the **Warning** from `/contact` response.

```bash
ffuf -u http://monitorsfour.htb/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -ac
```
- `-ac` | switch specifies auto-calibration, which filters out false positive responses

{{< screenshots "shot-003" >}}

Initially, the response appeared like a hint that the victim may be vulnerable to File Inclusion. 
But after some common LFI probes to `/contact` and `/Router`, no results were found of potential vulnerability.
However, `/Router.php` when tested in `burpsuite` all responses returned `200 OK`, meaning that requests were handled on the server.

{{< screenshots "shot-004" >}}

Additionally, `/user` returned an error message, stating that a token paramenter is missing.

{{< screenshots "shot-006" >}}

---
#### 004: Virtual Host

`/Router.php` was assumed to be a front controller, since it is explicitly named `Router` and calls a prefix path `/var/www/app/`, which basically implied a centralized request handler to other website components. 
Hence, with `ffuf` the victim was probed for hidden subdomains.

```bash
ffuf -u http://FUZZ.monitorsfour.htb/ -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac
```

Enumeration for DNS subdomains returned nothing.
But, then the logical next step was probing for any virtual host.
After few seconds virtual host `cacti` was found with a redirection status `302`.

```bash
ffuf -u http://FUZZ.monitorsfour.htb/ -H "Host: FUZZ.monitorsfour.htb" -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac
```
- `-H` | switch specifies virtual host fuzzing

{{< screenshots "shot-005" >}}

---
#### 005: IDOR

At this point, from what was found in `/user` the victim was vulnerable to IDOR.
As the error response suggested a missing parameter, `token=0` has been requested as a parameter in the URL and the target responded with sensitive credentials.

{{< screenshots "shot-007" >}}

---
#### 006: MD5 Decryption

`admin` user was the target user worth the most for further examination.
However, its password was encrypted with MD5.
- `56b32eb43e6f15395f6c46c1c9e1cd36`

Hence, https://iotools.cloud/tool/md5-decrypt/ successfully decrypted the found password resulting to a more sensible text.
- `wonderful1`

{{< screenshots "shot-008" >}}

---
#### 007: Cacti Login

The username `admin` along with the decrypted password `wonderful1` were entered in the `cacti` log in page, but the credentials denied access.
Regardless, since it was assumed that the cracked password was correct, the `name` of the `admin` user was entered as a username instead.
Which successfully allowed access to the `cacti` dashboard.
- `username: marcus`

{{< screenshots "shot-009" >}}

---
#### 008: Reverse Shell

According to `https://www.cvedetails.com/vulnerability-list/vendor_id-7458/product_id-12584/version_id-1907377/year-2025/opec-1/Cacti-Cacti-1.2.28.html` the target is vulnerable to RCE, labeled as `CVE-2025-24367`.

{{< screenshots "shot-010" >}}

A comprehensive POC against the vulnerability is found in `https://github.com/TheCyberGeek/CVE-2025-24367-Cacti-PoC`.
The steps for the reverse shell process on the attacker machine were straight forward