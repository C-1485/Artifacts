---
title: "TwoMillion"
draft: false
---

---

Nmap scan the target for available TCP ports

![nmap scan](/captures/screens/TwoMillion/shot-001.png)

---

To be able to view the website in browser the target IP must be resolved by creating a domain mapping in /etc/hosts

![/etc/hosts](/captures/screens/TwoMillion/shot-002.png)

---

We run burpsuite and examine the available path of the target under the 'target' tab

Under http://2million.htb/invite it is observed that an invite code is required for Sign Up

![/invite](/captures/screens/TwoMillion/shot-003.png)

After further examination of the website's source, under js/invite.min.js an eval based javascript packer obfuscation script is found in the response window of burpsuite.

![obfuscated script](/captures/screens/TwoMillion/shot-004.png)

Utilizing https://tunganhken.github.io/de4js/ the obfuscated JavaScript was deobfuscated and beautified, revealing functions that directly invoke backend API endpoints.

![beautified script](/captures/screens/TwoMillion/shot-005.png)

Then using curl a POST request is sent to the backend endpoint, with a ROT13 cipher 'data' value.

![rot13 cipher](/captures/screens/TwoMillion/shot-006.png)

https://cryptii.com/pipes/rot13-decoder is a web tool that helped with the decipher of the provided ROT13. 

The cipher's output:
- In order to generate the invite code, make a POST request to \/api\/v1\/invite\/generate

Thus, we test the newly found endpoint resulting to a base64 encoded 'code' value.

![base64 encoded](/captures/screens/TwoMillion/shot-007.png)

The encoded string can be decoded with https://www.base64decode.org/. 

The decoded string based on the generated base64 encoding:
- X43BI-41KBY-4HMSL-SYVEG

Once the decoded string is filled in the empty box of /invite, we get redirected to /register for registration. Next, the appropriate details are entered in /login and access to our personal /home page is granted.

![/home](/captures/screens/TwoMillion/shot-008.png)
