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
