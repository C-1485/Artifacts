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
#### 003: Virtual Hosts

As the `nmap` report showed that the application was running on nginx, additional reconnaissance for the discovery of hidden files and subdomains was made using `ffuf`.
`common.txt` wordlist exposed various paths, but what seemed most interesting was the **Warning** from `/contact` response.

{{< screenshots "shot-003" >}}

Initially, the response appeared like a hint that the victim may be vulnerable to File Inclusion. 
But after some common LFI probes to `/contact` and `/Router`, no results were found of potential vulnerability.
However, `/Router.php` when tested in `burpsuite` all responses returned `200 OK`, meaning that requests were handled on the server.

{{< screenshots "shot-004" >}}

Due to the absence of additional DNS records and the presence of generic content on the default host, virtual host enumeration was performed by fuzzing the Host header. This revealed an additional virtual host serving distinct content not accessible via standard DNS resolution.
