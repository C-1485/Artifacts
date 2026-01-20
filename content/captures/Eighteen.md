---
title: "Eighteen"
machine: Eighteen
tags: HackTheBox Machines
---
#### Write-Up for the HackTheBox Machine - Browsed
<!--more-->
---
#### 001: Port Scan

Initially a scan was performed against the victim to identify potential attack surfaces.

```bash
nmap -sC -sV -p- <victim_ip>
```

Based on the used command the scanner's report provides three open ports that could be used against the target.
- `80 : Microsoft IIS`
- `1433 : Microsoft SQL Server 2022`
- `5985 : Microsoft HTTPAPI (WinRM)`

{{< screenshots "shot-001" >}}

---
#### 002: Hostname Mapping

A DNS does not resolve the victim's IP, thus a mapping must be added in `/etc/hosts` to be able to browse the hostname `eighteen.htb` as found from the `nmap` scan.

---
#### 003: Port 80 Enumeration

User sessions expire after a short period of inactivity, redirecting to the `/login` page. 
Previously registered credentials can not be reused, indicating non-persistent or session-bound user storage rather than a proper backend account system.
Regardless after many attempts to log in with the previously registered credentials an error exposes a Microsoft SQL Server message related to duplicate key violation.
- `dbo.users : The duplicate key value is (c@c.com). (2627)`

{{< screenshots "shot-002" >}}

---
#### 004: Port 1433 Enumeration

Given that Microsoft SQL Server 2022 is open and the credentials `kevin:iNa2we6haRj2gaw!`, a Python script is utilized for server connectivity.

```bash
find / -name mssqlclient.py 2>/dev/null
```
```bash
python3 mssqlclient.py 'kevin:iNa2we6haRj2gaw!@<victim_ip>'
```

{{< screenshots "shot-003" >}}

A handful of databases are available on the victim, however out of all the one that seems most interesting is `financial_planner`.
Although as the current user `kevin` permission to use the database is not sufficient.

```bash
select name from sys.databases;
```
```bash
use financial_planner;
```

{{< screenshots "shot-004" >}}

As a subsequent step the SQL server is examined for potential users that can be leveraged.
There are three noticeable users, but only one can be impersonated and effectively execute privileged queries on the target SQL server.
- `appdev`



---
