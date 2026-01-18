---
title: "Eighteen"
machine: Eighteen
tags: HackTheBox Machines
---
#### Write-Up for the HackTheBox Machine - Browsed
<!--more-->
---
#### 001: Port Enumeration

Initially a `nmap` scan was performed against the victim to identify potential attack surfaces.

```bash
nmap -sC -sV -p- <victim_ip>
```

Based on the used command the `nmap` report provided three open ports that could be used against the target.
- `80 - Microsoft IIS`
- `1433 - Microsoft SQL Server 2022`
- `5985 - Microsoft HTTPAPI (WinRM)`

{{< screenshots "shot-001" >}}

---
#### 002: Hostname Mapping

A DNS does not resolve the victim's IP, thus a mapping must be added in `/etc/hosts` to be able to browse the hostname `eighteen.htb` as found from the `nmap` scan.


#### 003:

#### 004: