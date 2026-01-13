---
title: "Browsed"
machine: Browsed
tags: HackTheBox Machines
draft: true
---
#### Write-Up for the HackTheBox Machine - Browsed
<!--more-->
---
#### 001: Port Scan

The provided victim IP `10.10.8.1` was scanned with `nmap`. Available port found are `port 22` and `port 80`.

```bash
nmap -sC -sV -p- 10.10.8.1
```

{{< screenshots "shot-001" >}}

---
#### 002: Host Mapping

To be able to browse the target an IP:Hostname mapping should be made in `/etc/hosts`.
As commonly used by HackTheBox the target was named `<victim_machine>.htb` and its home page was viewed in browser.

{{< screenshots "shot-002" >}}

{{< screenshots "shot-003" >}}

---
#### 003: 