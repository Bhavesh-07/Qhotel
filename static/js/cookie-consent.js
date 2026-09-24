/**
 * Q Hotels - Privacy & Cookie Consent Management
 * Implements: Google Consent Mode v2, Global Privacy Control (GPC), and CCPA opt-out preferences
 */
(function () {
    var CONSENT_KEY = 'qhotels_cookie_consent';

    function checkGpcSignal() {
        return (
            window.navigator.globalPrivacyControl === true ||
            window.navigator.globalPrivacyControl === '1' ||
            window.globalPrivacyControl === true
        );
    }

    function updateGoogleConsent(status) {
        if (typeof window.gtag === 'function') {
            window.gtag('consent', 'update', {
                'analytics_storage': status === 'accepted' ? 'granted' : 'denied',
                'ad_storage': status === 'accepted' ? 'granted' : 'denied'
            });
        }
    }

    function setConsent(status) {
        try {
            localStorage.setItem(CONSENT_KEY, status);
        } catch (e) {
            console.warn('Unable to access localStorage for cookie consent:', e);
        }
        updateGoogleConsent(status);
        hideBanner();
    }

    function hideBanner() {
        var banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }

    function showBanner() {
        var banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'block';
        }
    }

    // Initialize consent state based on GPC signal or existing choice
    var isGpc = checkGpcSignal();
    var storedConsent = null;
    try {
        storedConsent = localStorage.getItem(CONSENT_KEY);
    } catch (e) {}

    if (isGpc) {
        // Automatically enforce opt-out when GPC signal is broadcasted
        updateGoogleConsent('rejected');
    } else if (storedConsent === 'accepted') {
        updateGoogleConsent('accepted');
    } else if (storedConsent === 'rejected') {
        updateGoogleConsent('rejected');
    }

    document.addEventListener('DOMContentLoaded', function () {
        var banner = document.getElementById('cookie-consent-banner');
        
        // Show banner only if no consent preference is stored and GPC is not active
        if (!storedConsent && !isGpc && banner) {
            showBanner();
        }

        var acceptBtn = document.getElementById('cookie-consent-accept');
        var rejectBtn = document.getElementById('cookie-consent-reject');
        var prefLinks = document.querySelectorAll('#open-cookie-preferences, .open-cookie-preferences');

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

        if (prefLinks && prefLinks.length > 0) {
            prefLinks.forEach(function (link) {
                link.addEventListener('click', function (e) {
                    e.preventDefault();
                    showBanner();
                });
            });
        }
    });
})();
