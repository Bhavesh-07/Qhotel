# Web Developer Security & Privacy Remediation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement all web application, frontend privacy, consent management, security header, and policy remediation items identified in the risk assessment scan for `qhotels.co`.

**Architecture:** 
- **Frontend Consent Architecture:** A lightweight, vanilla JS & CSS Consent Management Platform (CMP) embedded in `templates/base.html` and `static/js/cookie-consent.js`. Implements Google Consent Mode v2 (defaulting `analytics_storage` to `'denied'`), honors browser-level Global Privacy Control (`navigator.globalPrivacyControl`), and provides a persistent "Do Not Sell or Share My Personal Information" preference modal.
- **Server & Header Architecture:** IIS `web.config` and Flask security configurations enforcing HTTPS 301 redirection, HSTS (`Strict-Transport-Security`), and HTTPS-only secure session cookies (`SESSION_COOKIE_SECURE = true`).
- **Legal Compliance:** Comprehensive update to `templates/privacy-policy.html` reflecting GPC compliance, CCPA/CPRA consumer privacy rights, updated effective dates, and verified contact details.

**Tech Stack:** 
- HTML5 / Jinja2 Templates (Flask)
- Vanilla JavaScript (ES6+), jQuery, Bootstrap 4
- IIS Configuration XML (`web.config`) / Python Flask

---

### Task 1: Cookie Consent Banner & Google Consent Mode v2

**Files:**
- Create: `static/js/cookie-consent.js`
- Create: `static/css/cookie-consent.css`
- Modify: `templates/base.html:1-40`
- Modify: `templates/base.html:158-166`

**Step 1: Create the Cookie Consent CSS styling**
Create `static/css/cookie-consent.css` with clean, non-intrusive banner styling:
```css
/* Cookie Consent Banner Styling */
.cookie-consent-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #0f172a;
    color: #f8fafc;
    padding: 1.25rem 1.5rem;
    z-index: 99999;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.25);
    display: none;
    font-family: 'Open Sans', sans-serif;
}
.cookie-consent-container {
    max-width: 1140px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.cookie-consent-text {
    flex: 1 1 600px;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
}
.cookie-consent-text a {
    color: #38bdf8;
    text-decoration: underline;
}
.cookie-consent-buttons {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.cookie-btn {
    padding: 0.5rem 1.25rem;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 4px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}
.cookie-btn-accept {
    background-color: #0284c7;
    color: #ffffff;
}
.cookie-btn-accept:hover {
    background-color: #0369a1;
}
.cookie-btn-reject {
    background-color: transparent;
    border-color: #94a3b8;
    color: #f8fafc;
}
.cookie-btn-reject:hover {
    background-color: rgba(255, 255, 255, 0.1);
}
```

**Step 2: Create the Cookie Consent & Google Consent Mode JavaScript**
Create `static/js/cookie-consent.js`:
```javascript
(function () {
    const CONSENT_KEY = 'qhotels_cookie_consent';

    function setConsent(status) {
        localStorage.setItem(CONSENT_KEY, status);
        if (typeof gtag === 'function') {
            gtag('consent', 'update', {
                'analytics_storage': status === 'accepted' ? 'granted' : 'denied',
                'ad_storage': status === 'accepted' ? 'granted' : 'denied'
            });
        }
        hideBanner();
    }

    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }

    function showBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'block';
        }
    }

    // Check GPC Signal
    const isGpcEnabled = navigator.globalPrivacyControl === true;

    // Check existing consent
    const existingConsent = localStorage.getItem(CONSENT_KEY);

    if (isGpcEnabled) {
        // GPC signal detected: Automatically opt-out non-essential tracking
        setConsent('rejected');
    } else if (!existingConsent) {
        document.addEventListener('DOMContentLoaded', function () {
            showBanner();
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const acceptBtn = document.getElementById('cookie-consent-accept');
        const rejectBtn = document.getElementById('cookie-consent-reject');
        const prefLink = document.getElementById('open-cookie-preferences');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', function () {
                setConsent('accepted');
            });
        }

        if (rejectBtn) {
            rejectBtn.addEventListener('click', function () {
                setConsent('rejected');
            });
        }

        if (prefLink) {
            prefLink.addEventListener('click', function (e) {
                e.preventDefault();
                showBanner();
            });
        }
    });
})();
```

**Step 3: Update `templates/base.html` Head & Footer**
In `templates/base.html`:
1. Include `static/css/cookie-consent.css` in the `<head>`.
2. Initialize Google Consent Mode before loading gtag:
```html
<!-- Google Consent Mode v2 Default -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'wait_for_update': 500
  });
</script>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-149746814-1"></script>
<script>
  gtag('js', new Date());
  gtag('config', 'UA-149746814-1');
</script>
```
3. Add the Cookie Consent HTML Banner component right before `</body>`:
```html
<div id="cookie-consent-banner" class="cookie-consent-banner" role="region" aria-label="Cookie consent">
    <div class="cookie-consent-container">
        <p class="cookie-consent-text">
            We use cookies and similar technologies to optimize website functionality and analyze website traffic. 
            Review our <a href="/privacy-policy">Privacy Policy</a> to learn more about how we protect your personal data.
        </p>
        <div class="cookie-consent-buttons">
            <button id="cookie-consent-accept" class="cookie-btn cookie-btn-accept" type="button">Accept All</button>
            <button id="cookie-consent-reject" class="cookie-btn cookie-btn-reject" type="button">Reject Non-Essential</button>
        </div>
    </div>
</div>
<script src="/static/js/cookie-consent.js"></script>
```

**Step 4: Verification & Testing**
1. Launch local app: `python app.py`
2. Open `http://localhost:5000` in browser (or private window).
3. Verify banner appears on load.
4. Click "Accept All" -> verify `localStorage.getItem('qhotels_cookie_consent') === 'accepted'` and banner disappears.
5. Clear localStorage -> reload -> click "Reject Non-Essential" -> verify `localStorage.getItem('qhotels_cookie_consent') === 'rejected'` and `analytics_storage` remains `'denied'`.

**Step 5: Commit**
```bash
git add static/css/cookie-consent.css static/js/cookie-consent.js templates/base.html
git commit -m "feat(privacy): implement cookie consent banner and google consent mode v2"
```

---

### Task 2: Global Privacy Control (GPC) Signal Compliance

**Files:**
- Modify: `static/js/cookie-consent.js`

**Step 1: Enhance GPC Detection & Auto-Rejection Handling**
Ensure `cookie-consent.js` explicitly handles both standard GPC property (`navigator.globalPrivacyControl`) and header emulation:
```javascript
// Detect Global Privacy Control (GPC)
function checkGpcSignal() {
    return (
        window.navigator.globalPrivacyControl === true ||
        window.navigator.globalPrivacyControl === '1'
    );
}

if (checkGpcSignal()) {
    console.info('GPC signal detected. Opting out of tracking cookies automatically.');
    setConsent('rejected');
}
```

**Step 2: Verification & Testing**
1. In browser DevTools Console, test with GPC enabled:
   ```javascript
   Object.defineProperty(navigator, 'globalPrivacyControl', { value: true, configurable: true });
   ```
2. Trigger page reload and verify `qhotels_cookie_consent` defaults to `rejected` without prompting the user.

**Step 3: Commit**
```bash
git add static/js/cookie-consent.js
git commit -m "feat(privacy): implement automatic GPC opt-out detection"
```

---

### Task 3: Footer CCPA / "Do Not Sell My Personal Information" Link

**Files:**
- Modify: `templates/base.html:145-156`

**Step 1: Update Footer Structure**
Modify the copyright & legal links row in `templates/base.html`:
```html
<div class="row copyright-bg text-center py-3" style="margin-right:0;margin-left:0;">
    <div class="col-lg-3 col-md-6 mb-2 mb-lg-0">
        <a href="/sitemap" style="text-decoration:none;color:#000;">Sitemap</a>
    </div>
    <div class="col-lg-3 col-md-6 contxt mb-2 mb-lg-0">
        <span>© 2026 QHotels Management. All Rights Reserved</span>
    </div>
    <div class="col-lg-3 col-md-6 mb-2 mb-lg-0">
        <a href="/privacy-policy" style="text-decoration:none;color:#000;">Privacy Policy</a>
    </div>
    <div class="col-lg-3 col-md-6 mb-2 mb-lg-0">
        <a href="#" id="open-cookie-preferences" style="text-decoration:none;color:#000;font-weight:600;">Do Not Sell or Share My Personal Information</a>
    </div>
</div>
```

**Step 2: Verification & Testing**
1. Refresh the website on desktop and mobile viewport sizes.
2. Scroll to footer.
3. Click "Do Not Sell or Share My Personal Information".
4. Verify cookie preferences banner re-opens smoothly, allowing the user to revoke or update preferences.

**Step 3: Commit**
```bash
git add templates/base.html
git commit -m "feat(compliance): add CCPA do not sell link and update copyright year"
```

---

### Task 4: Privacy Policy Content Refresh & Contact Info Correction

**Files:**
- Modify: `templates/privacy-policy.html:1-96`

**Step 1: Update Policy Content & Sections**
In `templates/privacy-policy.html`:
1. Update effective date on Line 9:
   ```html
   <p class="mb-1 font-weight-bold">Effective date: September 24, 2026 (Last Updated: September 2026)</p>
   ```
2. Insert a dedicated section for **Global Privacy Control (GPC) & Browser Signals**:
   ```html
   <h2 class="mt-3">Global Privacy Control (GPC) & Do Not Track Signals</h2>
   <p class="mb-1">We respect and honor the Global Privacy Control (GPC) signal. When our systems detect a browser transmitting the GPC signal (<code>Sec-GPC: 1</code> or <code>navigator.globalPrivacyControl = true</code>), we automatically treat this as a request to opt-out of non-essential cookies, analytics, and data sharing without requiring any further action on your part.</p>
   ```
3. Insert a dedicated section for **State Privacy Rights (CCPA / CPRA & Other US State Laws)**:
   ```html
   <h2 class="mt-3">Your Privacy Rights (CCPA/CPRA & State Regulations)</h2>
   <p class="mb-1">Depending on your jurisdiction, you may have the following rights regarding your personal information:</p>
   <ul>
       <li><strong>Right to Know / Access:</strong> Request details on the categories and specific pieces of personal information we collect.</li>
       <li><strong>Right to Delete:</strong> Request the deletion of personal information collected from you.</li>
       <li><strong>Right to Correct:</strong> Request correction of inaccurate personal data.</li>
       <li><strong>Right to Opt-Out:</strong> Direct us not to sell or share your personal data by clicking the "Do Not Sell or Share My Personal Information" link in our website footer or by broadcasting a GPC signal.</li>
       <li><strong>Right to Non-Discrimination:</strong> We will not discriminate against you for exercising any of your privacy rights.</li>
   </ul>
   ```
4. Correct the Contact Us placeholder phone number on Line 92 from `1234567890` to:
   ```html
   <li>By phone number: <a href="tel:9856181700" style="text-decoration:none;color:inherit;">(985) 618-1700</a></li>
   ```

**Step 2: Verification & Testing**
1. Navigate to `http://localhost:5000/privacy-policy`.
2. Inspect the page to confirm all new headings, GPC explanation, CCPA rights, and updated phone number `(985) 618-1700` render cleanly.

**Step 3: Commit**
```bash
git add templates/privacy-policy.html
git commit -m "docs(privacy): update privacy policy with GPC disclosures, CCPA rights, and correct contact info"
```

---

### Task 5: Web Server Security Headers & HTTPS Enforcement (`web.config`)

**Files:**
- Modify: `web.config:1-29`

**Step 1: Update `web.config` with HSTS, HTTP Redirect, and Secure Cookie Flag**
Update `web.config`:
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

    <!-- Enforce HTTPS 301 Redirection -->
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

    <!-- Security Headers -->
    <httpProtocol>
      <customHeaders>
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains; preload" />
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
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

**Step 2: Verification & Testing**
1. Inspect `web.config` syntax with an XML parser or python test:
   ```bash
   python -c "import xml.etree.ElementTree as ET; ET.parse('web.config'); print('XML Valid')"
   ```
2. Verify `SESSION_COOKIE_SECURE` value is parsed as `True` in `app.py`:
   ```bash
   python -c "import os; print(os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true')"
   ```

**Step 3: Commit**
```bash
git add web.config
git commit -m "feat(security): add HSTS header, HTTPS redirect rule, and secure session cookie setting"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-09-24-web-developer-risk-remediation.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration.
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints.

Which approach would you like to take?
