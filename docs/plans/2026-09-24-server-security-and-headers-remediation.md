# Server Security Headers & Infrastructure Port Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remediate all remaining infrastructure, network port, SSL/TLS, and server security findings identified across `qhotels.co`, `13.65.148.90`, `144.76.101.11`, and associated subdomains without requiring client intervention.

---

## Infrastructure Architecture & Asset Mapping

Live DNS resolution reveals that the findings map directly to **two primary server hosts**:

| Host / IP | Role | Operating System | Affected Findings in Scan |
| :--- | :--- | :--- | :--- |
| **`13.65.148.90`**<br>(`qhotels.co`, `www.qhotels.co`, `demo.qhotels.co`, `innrly.com`, `www.innrly.com`, `demo2.innrly.com`) | Primary Web & Application Server | Windows Server (IIS 8.5+ / Azure VM) | • MS SQL Exposed (Port 1433)<br>• Plain FTP Exposed across **all 7 hosts** (Port 21)<br>• HTTP without SSL/TLS on root domains |
| **`144.76.101.11`**<br>(`timeclock.innrly.com`, `demoapi.innrly.com`) | Secondary Backend / Database Server | Linux (Hetzner Host) | • MySQL Exposed (Port 3306) |
| **`20.46.232.174`** / **`3.33.251.168`** | Microservices & Edge Endpoints | Cloud / AWS / Azure | • HTTP without SSL/TLS on edge subdomains |

> **Key Discovery:** Because all 7 FTP findings resolve to `13.65.148.90`, disabling plain FTP on this single Windows Server **resolves all 7 FTP scan findings at once**.

---

## Implementation Tasks

### Task 1: Application-Level Security Headers & HTTPS 301 Redirection (`web.config`)

**Files:**
- Modify: `web.config:1-29`

**Step 1: Update `web.config` with Robust IIS Rules and Duplicate-Safe Headers**
Update `web.config` to enforce HTTP → HTTPS 301 redirection and include `<remove name="..."/>` elements before adding security headers to prevent IIS duplicate collection errors (HTTP 500.19):

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler"
           path="*"
           verb="*"
           modules="FastCgiModule"
           scriptProcessor="C:\inetpub\wwwroot\QhotelsLive\Qhotelspaython\venv\Scripts\python.exe|C:\inetpub\wwwroot\QhotelsLive\Qhotelspaython\venv\Lib\site-packages\wfastcgi.py"
           resourceType="Unspecified"
           requireAccess="Script" />
    </handlers>

    <!-- Enforce HTTPS 301 Permanent Redirection -->
    <rewrite>
      <rules>
        <rule name="HTTP to HTTPS redirect" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="off" ignoreCase="true" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>

    <!-- Security Response Headers (with duplicate protection) -->
    <httpProtocol>
      <customHeaders>
        <remove name="Strict-Transport-Security" />
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains; preload" />
        <remove name="X-Content-Type-Options" />
        <add name="X-Content-Type-Options" value="nosniff" />
        <remove name="X-Frame-Options" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
        <remove name="Referrer-Policy" />
        <add name="Referrer-Policy" value="strict-origin-when-cross-origin" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>

  <appSettings>
    <add key="PYTHONPATH" value="C:\inetpub\wwwroot\QhotelsLive\Qhotelspaython" />
    <add key="WSGI_HANDLER" value="app.app" />
    <add key="WSGI_LOG" value="C:\inetpub\wwwroot\QhotelsLive\Qhotelspaython\logs\wfastcgi.log" />
    <add key="FLASK_SECRET_KEY" value="temp-secret-key-change-this" />
    <add key="ADMIN_BOOTSTRAP_USERNAME" value="admin" />
    <add key="ADMIN_BOOTSTRAP_PASSWORD" value="Admin@12345" />
    <add key="SESSION_COOKIE_SECURE" value="true" />
    <add key="DB_HOST" value="127.0.0.1" />
    <add key="DB_USER" value="bhavik" />
    <add key="DB_PASSWORD" value="33jain33" />
    <add key="DB_NAME" value="qhotels_db" />
  </appSettings>
</configuration>
```

**Step 2: Validate XML Syntax**
Run:
```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('web.config'); print('web.config XML Valid')"
```
Expected output: `web.config XML Valid`

**Step 3: Commit and Push**
```bash
git add web.config
git commit -m "feat(security): add HTTPS 301 redirect, HSTS header, and secure session cookie in web.config"
git push origin main
```

---

### Task 2: Block Public MS SQL Port 1433 on Windows Server (`13.65.148.90`)

**Target Host:** `13.65.148.90` (Azure Windows Server)

**Step 1: Execute Windows Firewall Inbound Rule via PowerShell (Admin)**
Connect to `13.65.148.90` via Remote Desktop (RDP) or Azure Run Command and execute:
```powershell
# Create or update inbound firewall rule to block public internet access on Port 1433
New-NetFirewallRule -DisplayName "Block Public MS SQL (Port 1433)" `
    -Direction Inbound `
    -LocalPort 1433 `
    -Protocol TCP `
    -Action Block `
    -RemoteAddress Any
```
*(If internal services on Azure subnet need to reach MS SQL, replace `-RemoteAddress Any` with specific Azure VNet subnet range e.g., `10.0.0.0/16` or office static IPs).*

**Step 2: Verification from External Machine**
From an external terminal:
```powershell
Test-NetConnection -ComputerName 13.65.148.90 -Port 1433
```
Expected output: `TcpTestSucceeded : False`

---

### Task 3: Block Public MySQL Port 3306 on Linux Host (`144.76.101.11`)

**Target Host:** `144.76.101.11` (Hetzner Linux Server)

**Step 1: Configure UFW / iptables Firewall & Localhost Binding via SSH**
SSH into `144.76.101.11` as root/admin:
```bash
# 1. Block public inbound traffic on Port 3306 via UFW
sudo ufw deny 3306/tcp

# 2. Alternatively via iptables (if UFW is not active)
sudo iptables -A INPUT -p tcp --dport 3306 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3306 -j DROP

# 3. Ensure MySQL only listens on localhost (127.0.0.1)
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mysql.conf.d/mysqld.cnf 2>/dev/null || true
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/my.cnf 2>/dev/null || true

# 4. Restart MySQL service
sudo systemctl restart mysql
```

**Step 2: Verification from External Machine**
From an external terminal:
```bash
nc -zv -w 3 144.76.101.11 3306
```
Expected output: Connection timed out / Connection refused.

---

### Task 4: Disable Plain Unencrypted FTP (Port 21) on Windows Host (`13.65.148.90`)

**Target Host:** `13.65.148.90` (Covers `qhotels.co`, `innrly.com`, and all 7 FTP findings)

**Step 1: Disable Microsoft FTP Service & Block Port 21**
On `13.65.148.90` (PowerShell Admin):
```powershell
# 1. Stop and disable Microsoft FTP Service
Stop-Service -Name "ftpsvc" -ErrorAction SilentlyContinue
Set-Service -Name "ftpsvc" -StartupType Disabled -ErrorAction SilentlyContinue

# 2. Block inbound Port 21 in Windows Firewall
New-NetFirewallRule -DisplayName "Block Plain FTP (Port 21)" `
    -Direction Inbound `
    -LocalPort 21 `
    -Protocol TCP `
    -Action Block
```

**Step 2: Verification across All 7 Hostnames**
From an external machine:
```powershell
Test-NetConnection -ComputerName qhotels.co -Port 21
Test-NetConnection -ComputerName innrly.com -Port 21
Test-NetConnection -ComputerName 13.65.148.90 -Port 21
```
Expected output: `TcpTestSucceeded : False` for all targets.

---

### Task 5: Enforce HTTPS & SSL Certificate Verification on Subdomains

**Target Endpoints:** `upload.qhotels.co`, `demo.qhotels.co`, `innrly.com`, `timeclock.innrly.com`, `scheduler.innrly.com`, etc.

**Step 1: Enable Cloudflare "Always Use HTTPS" / Edge SSL**
If subdomains use Cloudflare DNS:
1. In Cloudflare Dashboard → **SSL/TLS** → **Edge Certificates**.
2. Toggle **Always Use HTTPS** to **ON**.
3. Toggle **Automatic HTTPS Rewrites** to **ON**.

**Step 2: Verification**
Test HTTP response code for subdomains:
```powershell
(Invoke-WebRequest -Uri "http://qhotels.co" -MaximumRedirection 0 -ErrorAction SilentlyContinue).StatusCode
```
Expected output: `301` (Redirecting to `https://`).

---

## Action Checklist & Resolution Tracking

- [ ] **Task 1:** Apply and push `web.config` HTTPS 301 rewrite, HSTS, and duplicate-safe security headers.
- [ ] **Task 2:** Run PowerShell firewall command on `13.65.148.90` to block Port 1433.
- [ ] **Task 3:** Run UFW / bind-address commands on `144.76.101.11` to block Port 3306.
- [ ] **Task 4:** Stop and disable `ftpsvc` on `13.65.148.90` to resolve all 7 FTP findings.
- [ ] **Task 5:** Verify HTTP → HTTPS 301 redirection across endpoints.
