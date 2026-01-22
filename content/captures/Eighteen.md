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

Based on the used command the scanner's report provided three open ports that could be used against the target.
- `80 : Microsoft IIS`
- `1433 : Microsoft SQL Server 2022`
- `5985 : Microsoft HTTPAPI (WinRM)`

{{< screenshots "shot-001" >}}

---
#### 002: Hostname Mapping

A DNS does not resolve the victim's IP, thus a mapping must be added in `/etc/hosts` to be able to browse the hostname `eighteen.htb` as found from the `nmap` scan.

---
#### 003: Port 80 Enumeration

User sessions expire after a short period of inactivity, redirecting to the `/login` page. Previously registered credentials can not be reused, indicating non-persistent user storage rather than a proper backend account system. Regardless after many attempts to log in with the previously registered credentials an error exposes a Microsoft SQL Server message related to duplicate key violation.
- `dbo.users : The duplicate key value is (c@c.com). (2627)`

{{< screenshots "shot-002" >}}

---
#### 004: Port 1433 Enumeration

Given that Microsoft SQL Server 2022 is open and the credentials `kevin:iNa2we6haRj2gaw!`, a Python script was utilized for server connectivity.
```bash
find / -name mssqlclient.py 2>/dev/null
```
```bash
python3 mssqlclient.py 'kevin:iNa2we6haRj2gaw!@<victim_ip>'
```

{{< screenshots "shot-003" >}}

A handful of databases are available on the victim, however out of all the one that seemed most interesting is `financial_planner`. Although as the current user `kevin` permission to use the database is not sufficient.
```sql
SELECT name FROM sys.databases;
```
```bash
use financial_planner;
```

{{< screenshots "shot-004" >}}

As a subsequent step the SQL server is examined for potential users that can be leveraged. There are three noticeable users, but only one can be impersonated and effectively execute privileged queries on the target SQL server.
- `appdev`
```sql
SELECT loginname FROM syslogins;
```
```bash
enum_impersonate
```

The precedent inaccessible database becomes available when switching to the impersonated user. In `users` table within the `financial_planner` database a single entry is found with a hashed password.
- `pbkdf2:sha256:600000$AMtzteQIG7yAbZIa$0673ad90a0b4afb19d662336f0fce3a9edd0b7b19193717be28ce4d66c887133`
```sql
SELECT name FROM sys.tables;
```
```sql
SELECT * FROM users;
```

{{< screenshots "shot-005" >}}

---
#### 005: Hash Crack

The hashing function PBKDF2-HMAC-SHA256 is designed to be irreversible and computationally expensive. Nonetheless, a GitHub repository [Werkzeug-PBKDF2-Hash-Converter](https://github.com/qui113x/Werkzeug-PBKDF2-Hash-Converter) provides a concise conversion process, compatible for Hashcat. The execution of the script converted the salt and hex values to a Base64 encoding.
- `sha256:600000:QU10enRlUUlHN3lBYlpJYQ==:BnOtkKC0r7GdZiM28Pzjqe3Qt7GRk3F74ozk1myIcTM=`
```bash
git clone https://github.com/qui113x/Werkzeug-PBKDF2-Hash-Converter
```
```bash
python3 pbkdf2-hashconv.py
```

{{< screenshots "shot-006" >}}

According to the description of the found repository, the converted value was added in text file named `hash.txt`. Hashcat has successfully recovered a password with the use of the `rockyou.txt` wordlist and a set mode for PBKDF2-HMAC-SHA256.
- `sha256:600000:QU10enRlUUlHN3lBYlpJYQ==:BnOtkKC0r7GdZiM28Pzjqe3Qt7GRk3F74ozk1myIcTM=:iloveyou1`
```bash
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

{{< screenshots "shot-006" >}}

---
#### 006

---
#### 007