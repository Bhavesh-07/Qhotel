# Privacy & Cookie Compliance Risk Remediation Implementation Plan

**Goal:** Remediate all 6 medium-severity privacy findings from `risk_findings_2026-10-08_10-10-12.csv` across `qhotels.co` by adding a CCPA/CPRA "Do Not Sell" footer link, enforcing pre-consent blocking of non-necessary cookies, making GPC (Global Privacy Control) detection instantaneous, ensuring cookie banner scanner compatibility, and keeping the privacy policy current.

**Architecture:** Frontend privacy-first consent architecture utilizing Google Consent Mode v2, asynchronous cookie control initialized in `<head>` before any third-party scripts load, strict Global Privacy Control (`Sec-GPC` / `navigator.globalPrivacyControl`) signal enforcement, and accessible preference management controls.

**Tech Stack:** Python 3.10+ / Flask, Jinja2, Vanilla JavaScript (ES6+), CSS3, HTML5 ARIA compliant markup.

---

### Task 1: Add "Do Not Sell or Share My Personal Information" Link to Footer

**Files:**
- Modify: `templates/base.html:188-199`
- Modify: `static/css/custom.css` (or `static/css/cookie-consent.css`)

**Step 1: Inspect footer structure in `templates/base.html`**
Verify the copyright / footer link row.

**Step 2: Update footer navigation links in `templates/base.html`**
Replace the 3-column copyright row with a 4-column (or balanced flex/grid) layout that includes the mandatory CCPA/CPRA opt-out anchor:

```html
<div class="row copyright-bg text-center py-3" style="margin-right:0;margin-left:0;">
    <div class="col-md-3 col-sm-6 mb-2 mb-md-0">
        <a href="/sitemap" style="text-decoration:none;color:#000;">Sitemap</a>
    </div>
    <div class="col-md-3 col-sm-6 mb-2 mb-md-0">
        <a href="#" class="open-cookie-preferences" id="open-cookie-preferences" style="text-decoration:none;color:#000;">Do Not Sell or Share My Personal Information</a>
    </div>
    <div class="col-md-3 col-sm-6 mb-2 mb-md-0">
        <a href="/privacy-policy" style="text-decoration:none;color:#000;">Privacy Policy</a>
    </div>
    <div class="col-md-3 col-sm-6 contxt">
        <span>© 2026 QHotels Management. All Rights Reserved</span>
    </div>
</div>
```

**Step 3: Verify link click triggers the Cookie Consent / Preferences banner**
Check that clicking `#open-cookie-preferences` displays the `#cookie-consent-banner` modal smoothly.

---

### Task 2: Reorder Head Scripts & Enforce Pre-Consent Blocking (Zero Pre-Consent Tracking)

**Files:**
- Modify: `templates/base.html:34-50`
- Modify: `static/js/cookie-consent.js`

**Step 1: Move Consent Initialization and GPC check to top of `<head>`**
In `templates/base.html`, place `cookie-consent.js` (or an inline immediate bootstrap) before any analytics scripts so that `gtag('consent', 'default', ...)` and GPC evaluations occur synchronously before network dispatch.

```html
<!-- Cookie Consent Management & GPC Initializer -->
<script src="/static/js/cookie-consent.js"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    
    // Set default consent to DENIED for all categories
    gtag('consent', 'default', {
        'analytics_storage': 'denied',
        'ad_storage': 'denied',
        'ad_user_data': 'denied',
        'ad_personalization': 'denied',
        'wait_for_update': 500
    });
</script>
```

**Step 2: Conditional Tag Execution**
Ensure Google Analytics (`gtag.js`) only fires if consent is explicitly `'accepted'` or defaults to strict anonymized/denied mode without sending personal identifiers.

**Step 3: Verification**
Open browser devtools Network and Application tabs. Ensure zero tracking cookies (`_ga`, `_gid`) are set upon initial page landing before clicking "Accept All".

---

### Task 3: Strengthen Global Privacy Control (GPC) Automated Signal Handling

**Files:**
- Modify: `static/js/cookie-consent.js`

**Step 1: Update GPC Signal Detection Function**
Ensure `cookie-consent.js` detects all variations of the GPC API across modern browsers (Firefox, Brave, Chrome extensions, DuckDuckGo):

```javascript
function checkGpcSignal() {
    return (
        window.navigator.globalPrivacyControl === true ||
        window.navigator.globalPrivacyControl === '1' ||
        window.globalPrivacyControl === true ||
        document.globalPrivacyControl === true
    );
}
```

**Step 2: Enforce Automatic Rejection upon GPC Detection**
When `checkGpcSignal()` returns `true`:
- Immediately call `updateGoogleConsent('rejected')`.
- Suppress or hide the persistent opt-in popup banner (or display an informative status: *"Global Privacy Control signal detected. Non-essential tracking disabled."*).
- Ensure no marketing or analytical cookies are generated.

**Step 3: Verification**
Test with `navigator.globalPrivacyControl = true` in browser console; verify `gtag('consent', 'update', { analytics_storage: 'denied', ... })` is dispatched immediately.

---

### Task 4: Enhance Cookie Banner Scanner Detectability & Accessibility (ARIA)

**Files:**
- Modify: `templates/base.html:202-218`
- Modify: `static/css/cookie-consent.css`

**Step 1: Add Standardized Scanner Metadata & ARIA Attributes**
Update the banner markup in `templates/base.html` so automated compliance crawlers (e.g. Coalition, OneTrust, Termly scanner engines) easily classify the CMP element:

```html
<!-- Cookie Consent Banner -->
<div id="cookie-consent-banner" 
     class="cookie-consent-banner" 
     role="dialog" 
     aria-modal="false" 
     aria-label="Cookie and Privacy Consent" 
     data-cmp="qhotels-consent-manager" 
     data-nosnippet="true">
    <div class="cookie-consent-container">
        <div class="cookie-consent-text">
            <p>
                We use cookies and similar tracking technologies to analyze traffic, enhance performance, and respect your privacy choices. 
                Under applicable privacy laws (including CCPA/CPRA), you have the right to opt out of data sharing. 
                Review our <a href="/privacy-policy">Privacy Policy</a> or manage your preferences.
            </p>
        </div>
        <div class="cookie-consent-buttons">
            <button id="cookie-consent-accept" class="cookie-btn cookie-btn-accept" type="button" aria-label="Accept all cookies">Accept All</button>
            <button id="cookie-consent-reject" class="cookie-btn cookie-btn-reject" type="button" aria-label="Reject non-essential cookies">Reject Non-Essential</button>
        </div>
    </div>
</div>
```

**Step 2: Ensure Seamless Responsiveness & Contrast**
Verify CSS styles in `static/css/cookie-consent.css` maintain WCAG AA color contrast ratios (e.g. background `#0f172a`, text `#f8fafc`, buttons clearly distinct).

---

### Task 5: Privacy Policy Disclosures & Date Synchronization

**Files:**
- Modify: `templates/privacy-policy.html:8-12`

**Step 1: Verify Policy Effective Date & Disclosures**
Update the effective date to October 2026:
```html
<p class="mb-1 font-weight-bold">Effective date: October 8, 2026 (Last Updated: October 2026)</p>
```

**Step 2: Verify Explicit Alignment with Findings**
Confirm `templates/privacy-policy.html` contains:
1. Clear statement regarding Global Privacy Control (GPC) recognition (Section: *Global Privacy Control (GPC) & Do Not Track Signals*).
2. Explicit CCPA/CPRA opt-out instructions and clickable `#open-cookie-preferences-policy` anchor.
3. Affirmation that the business does not sell personal data for monetary consideration.

---

## Plan Completion & Handoff

Plan complete and saved to `docs/plans/2026-10-08-privacy-risk-remediation.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints.

Which approach?
