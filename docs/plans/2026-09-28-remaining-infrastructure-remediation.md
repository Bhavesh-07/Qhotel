# Infrastructure & Server Risk Remediation Implementation Plan

> **For Claude / DevOps Engineers:** Implementation plan for completing all remaining Phase 1 infrastructure, port hardening, and web server security remediations.

**Goal:** Secure database ports (MS SQL & MySQL), disable legacy cleartext FTP, and enforce system-wide HTTPS 301 redirection and HSTS security headers across all servers (`13.65.148.90`, `144.76.101.11`, `qhotels.co`, `innrly.com`).

**Architecture:** Multi-server network hardening covering Windows Server 2016/2019/2022 (IIS 8.5+ on Azure VM `13.65.148.90`), Linux Server (Ubuntu/Debian on Hetzner `144.76.101.11`), and Edge CDN/DNS (Cloudflare / IIS URL Rewrite).

**Tech Stack:** PowerShell, Windows Defender Firewall, Netsh, Azure NSG, Linux UFW / iptables, MySQL 8.x / MariaDB, Microsoft IIS 8.5+ URL Rewrite & HTTP Protocol Modules.

---

## Asset & Finding Mapping

| Task # | Target Asset | Service / Port | Operating System | Primary Action |
| :--- | :--- | :--- | :--- | :--- |
| **Task 1** | `13.65.148.90` | MS SQL (`1433`) | Windows Server / Azure VM | Inbound Firewall Block + Azure NSG Inbound rule restriction |
| **Task 2** | `144.76.101.11` | MySQL (`3306`) | Linux (Ubuntu/Debian Hetzner) | Localhost binding (`127.0.0.1`) + UFW/iptables inbound drop |
| **Task 3** | `13.65.148.90` (7 hosts) | FTP (`21`) | Windows Server | Disable Microsoft FTP Service (`ftpsvc`) + Block Port 21 |
| **Task 4** | All web endpoints | HTTP (`80` ➔ `443`) | IIS 8.5+ / Cloudflare | 301 Permanent Redirect Rule in `web.config` & Edge CDN |
| **Task 5** | `web.config` / IIS | Security Headers | IIS 8.5+ | Enforce `Strict-Transport-Security` (HSTS) with duplicate removal |

---

## Detailed Implementation Tasks

### Task 1: Close Public Access to MS SQL Server (Port 1433)

**Target Host:** `13.65.148.90` (Azure Windows Server / Primary Host)

#### Step 1.1: Block Inbound Port 1433 via Windows Defender Firewall
Connect to `13.65.148.90` via Remote Desktop (RDP) or Azure Run Command and run PowerShell as Administrator:

```powershell
# 1. Remove any existing overly permissive rules for Port 1433
Remove-NetFirewallRule -DisplayName "*SQL*" -ErrorAction SilentlyContinue

# 2. Add Inbound Block rule for public internet access
New-NetFirewallRule -DisplayName "Block Public MS SQL (Port 1433)" `
    -Description "Remediation for Risk Scan Finding: MS SQL Exposed" `
    -Direction Inbound `
    -LocalPort 1433 `
    -Protocol TCP `
    -Action Block `
    -Profile Any `
    -Enabled True

# 3. (Optional) Allow specific internal subnet/VPN IP if application requires backend access
# New-NetFirewallRule -DisplayName "Allow Internal App MS SQL" -Direction Inbound -LocalPort 1433 -Protocol TCP -Action Allow -RemoteAddress "10.0.0.0/16","<OFFICE_STATIC_IP>"
```

#### Step 1.2: Restrict Inbound NSG in Azure Portal (Cloud Level)
1. Navigate to **Azure Portal** ➔ **Virtual Machines** ➔ `13.65.148.90` VM ➔ **Networking**.
2. Locate any Inbound security rule allowing Port `1433` from source `Any` / `*`.
3. Change Source to **`VirtualNetwork`** or delete the rule if external connectivity is not needed.

#### Step 1.3: Verification from External Machine
Run from any external computer:
```powershell
Test-NetConnection -ComputerName 13.65.148.90 -Port 1433
```
* **Expected Output:** `TcpTestSucceeded : False` (Port is filtered/closed).

---

### Task 2: Close Public Access to MySQL Server (Port 3306)

**Target Host:** `144.76.101.11` (Hetzner Linux Server / `timeclock.innrly.com`)

#### Step 2.1: Bind MySQL to Localhost (`127.0.0.1`)
Connect via SSH to `144.76.101.11`:
```bash
# 1. Edit MySQL configuration to listen only on loopback interface
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mysql.conf.d/mysqld.cnf 2>/dev/null || true
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/my.cnf 2>/dev/null || true
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mariadb.conf.d/50-server.cnf 2>/dev/null || true

# 2. Restart MySQL / MariaDB service
sudo systemctl restart mysql || sudo systemctl restart mariadb
```

#### Step 2.2: Enforce Host-Level Firewall Blocking (UFW / iptables)
```bash
# Using UFW (if enabled)
sudo ufw deny 3306/tcp
sudo ufw reload

# Using iptables directly
sudo iptables -C INPUT -p tcp --dport 3306 -s 127.0.0.1 -j ACCEPT 2>/dev/null || sudo iptables -I INPUT 1 -p tcp --dport 3306 -s 127.0.0.1 -j ACCEPT
sudo iptables -C INPUT -p tcp --dport 3306 -j DROP 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 3306 -j DROP
```

#### Step 2.3: Verification from External Machine
Run from an external terminal:
```bash
nc -zv -w 3 144.76.101.11 3306
# Or PowerShell:
Test-NetConnection -ComputerName 144.76.101.11 -Port 3306
```
* **Expected Output:** `TcpTestSucceeded : False` or `Connection timed out` / `Connection refused`.

---

### Task 3: Disable Plain FTP (Port 21) Across All Hosts & Enforce SFTP/FTPS

**Target Host:** `13.65.148.90` (Covers `qhotels.co`, `innrly.com`, `demo.qhotels.co`, and all 7 FTP findings)

#### Step 3.1: Stop and Disable Microsoft FTP Service
On `13.65.148.90` (PowerShell as Administrator):
```powershell
# 1. Check if Microsoft FTP service is running
Get-Service -Name "ftpsvc" -ErrorAction SilentlyContinue

# 2. Stop and disable the service
Stop-Service -Name "ftpsvc" -ErrorAction SilentlyContinue
Set-Service -Name "ftpsvc" -StartupType Disabled -ErrorAction SilentlyContinue

# 3. Add Inbound Block rule for Port 21
New-NetFirewallRule -DisplayName "Block Plain FTP (Port 21)" `
    -Description "Remediation for Risk Scan Finding: FTP Service without SSL/TLS" `
    -Direction Inbound `
    -LocalPort 21 `
    -Protocol TCP `
    -Action Block `
    -Profile Any `
    -Enabled True
```

#### Step 3.2: Switch File Management Workflows to SFTP (Port 22) / Web Deploy
- If developers or administrators require remote file updates, configure **OpenSSH for Windows** (SFTP on Port 22) with public key authentication or use Git deployment workflows.

#### Step 3.3: Verification Across All 7 Hostnames
Run from an external machine:
```powershell
$targets = @("13.65.148.90", "qhotels.co", "www.qhotels.co", "demo.qhotels.co", "innrly.com", "www.innrly.com", "demo2.innrly.com")
foreach ($t in $targets) {
    $res = Test-NetConnection -ComputerName $t -Port 21 -WarningAction SilentlyContinue
    [PSCustomObject]@{ Target = $t; Port21Open = $res.TcpTestSucceeded }
}
```
* **Expected Output:** `Port21Open : False` for all 7 hostnames.

---

### Task 4 & Task 5: Configure 301 HTTP ➔ HTTPS Redirection & HSTS Headers in IIS

**Target Files:**
- Modify: [`web.config`](file:///c:/wamp64/www/qhotel/web.config)

#### Step 4.1: Ensure IIS URL Rewrite & Header Modules are Configured
Verify that [`web.config`](file:///c:/wamp64/www/qhotel/web.config) contains the complete rewrite rule and duplicate-safe security response headers:

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

    <!-- 1. Enforce HTTPS 301 Permanent Redirection -->
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

    <!-- 2. Security Response Headers (with duplicate protection) -->
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

#### Step 4.2: Edge HTTPS Enforcement (Cloudflare / DNS Level)
For hostnames routed via Cloudflare or CDN:
1. Log in to **Cloudflare Dashboard** ➔ Select Domain (`qhotels.co` / `innrly.com`).
2. Go to **SSL/TLS** ➔ **Edge Certificates**.
3. Turn **ON** `Always Use HTTPS`.
4. Turn **ON** `Automatic HTTPS Rewrites`.
5. Under **HSTS**, enable Status: `Active`, `Max-Age: 12 months`, `Include subdomains: Yes`, `Preload: Yes`.

#### Step 4.3: Verification of Redirection & HSTS
Execute PowerShell command to inspect HTTP response headers:
```powershell
# 1. Verify 301 Redirect on plain HTTP
$redirectTest = Invoke-WebRequest -Uri "http://qhotels.co" -MaximumRedirection 0 -ErrorAction SilentlyContinue
Write-Host "HTTP Status:" $redirectTest.StatusCode "(Expected: 301)"
Write-Host "Redirect Location:" $redirectTest.Headers.Location

# 2. Verify HSTS header on HTTPS
$httpsTest = Invoke-WebRequest -Uri "https://qhotels.co" -Method Head -ErrorAction SilentlyContinue
Write-Host "HSTS Header:" $httpsTest.Headers["Strict-Transport-Security"]
```
* **Expected Output:**
  - Status Code: `301`
  - Location: `https://qhotels.co/`
  - `Strict-Transport-Security`: `max-age=31536000; includeSubDomains; preload`

---

## Rollback & Troubleshooting Procedures

### 1. Database Connection Failure
- **Symptom:** Web application reports "Cannot connect to database".
- **Cause:** Localhost binding or firewall blocked application connection.
- **Fix:** Verify application connects to `127.0.0.1` locally rather than public IP. If application is hosted on a separate server, whitelist the specific application server IP in the firewall rather than leaving port open to `0.0.0.0/0`.

### 2. IIS HTTP 500.19 on `web.config` Deployment
- **Symptom:** IIS returns HTTP 500.19 (Internal Server Error / Duplicate custom headers).
- **Fix:** Ensure `<remove name="..." />` is included before each `<add name="..." />` tag in `<customHeaders>`, and verify that IIS **URL Rewrite Module 2.1** is installed on Windows Server.

---

## Completion Checklist

- [x] **1. MS SQL (Port 1433):** Windows Firewall inbound block applied on `13.65.148.90` (Verified: `TcpTestSucceeded : False`).
- [x] **2. MySQL (Port 3306):** Localhost binding & external access verified closed on `144.76.101.11` and `13.65.148.90` (Verified: `TcpTestSucceeded : False`).
- [x] **3. FTP (Port 21):** FileZilla service & `ftpsvc` stopped/disabled on `13.65.148.90` (Verified closed across all 7 hosts: `qhotels.co`, `innrly.com`, `13.65.148.90`, etc.).
- [x] **4. HTTPS 301 Redirection:** Verified across all hostnames (`http://` ➔ `https://`).
- [x] **5. HSTS Header:** Verified active in `web.config` and live HTTP response (`Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`).
- [x] **6. Update Tracker:** All 10 items marked as complete in [`RISK_REMEDIATION_PLAN.md`](file:///c:/wamp64/www/qhotel/RISK_REMEDIATION_PLAN.md).
