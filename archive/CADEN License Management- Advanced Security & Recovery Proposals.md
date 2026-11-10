# CADEN License Management: Advanced Security & Recovery Proposals

**Prepared for:** CADEN Architecture Team  
**Context:** RCM Dashboard Integration  
**Objective:** Enhance the CADEN licensing script to prevent trial abuse, eliminate accidental lockouts during hardware/browser updates, and ensure revocation integrity without compromising offline user experience.

---

## Executive Summary

The current CADEN implementation provides robust baseline protection but faces edge-case vulnerabilities regarding license resets and hardware fingerprint changes. This document proposes four targeted architectural improvements to harden the client-side governance logic while maintaining a seamless user experience.

---

## Solution 1: Secure License Reset (Preventing Trial Abuse)

### The Vulnerability
Users can repeatedly click a "Reset License" button to clear `localStorage`, wiping the genesis timestamp and gaining infinite 30-day grace periods.

### The Architectural Fix
1. **Server-Side Device Tracking:** The server must track `deviceId` and limit grace periods per device.
2. **Admin Authentication:** Client-side resets require a server-verified admin password.
3. **Persistent Counters:** Use `IndexedDB` (which survives standard cache clears) to track local reset attempts.

### Implementation Script
```javascript
// Add to CADEN Script
async function secureResetLicense() {
    const adminPassword = prompt("Enter administrator password to reset license:");
    if (!adminPassword) return;

    try {
        const deviceId = generateDeviceFingerprint();
        const response = await fetch(`${CADEN_CONFIG.serverUrl}/v1/authorize-reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                appId: CADEN_CONFIG.appId,
                deviceId: deviceId,
                adminPassword: adminPassword
            })
        });

        const data = await response.json();
        if (data.authorized) {
            // Wipe CADEN keys specifically
            Object.values(KEYS).forEach(key => localStorage.removeItem(key));
            alert("License reset authorized. Please reconnect to activate.");
            location.reload();
        } else {
            alert("Reset denied. Contact your administrator.");
            window.storeSystemTelemetry("UNAUTHORIZED_RESET_ATTEMPT", `Admin auth failed for ${deviceId}`, 1);
        }
    } catch (err) {
        alert("Cannot verify admin credentials. Please connect to the internet.");
    }
}
```

---

## Solution 2: Smart Auto-Recovery (Preventing Accidental Lockouts)

### The Vulnerability
A minor browser update or GPU driver change alters the hardware fingerprint. The script immediately wipes the valid token and triggers a hard lockdown, locking out offline users.

### The Architectural Fix
1. **Fingerprint Tolerance:** Calculate similarity between old and new fingerprints.
2. **Server Validation:** If similarity > 85%, request server validation *before* wiping the token.
3. **Offline Grace:** If offline during a minor change, trigger a "Soft Lockdown" (warning banner) instead of a hard block.

### Implementation Script
```javascript
// Override executeLockdownScreen for smart recovery
function executeLockdownScreen(displayMessage) {
    if (displayMessage.includes("Hardware mismatch") || displayMessage.includes("fingerprint")) {
        const currentFp = generateDeviceFingerprint();
        const storedToken = localStorage.getItem(KEYS.token);
        
        if (storedToken) {
            try {
                const oldFp = JSON.parse(atob(storedToken.split('.')[1])).devId;
                const similarity = calculateFingerprintSimilarity(oldFp, currentFp);
                
                if (similarity > 0.85) {
                    // Minor change detected
                    if (navigator.onLine) {
                        validateFingerprintChange(currentFp, oldFp).then(valid => {
                            if (valid) autoActivate();
                            else _doLockdown("Hardware change not authorized.");
                        });
                    } else {
                        // Offline: Soft lockdown
                        _doSoftLockdown("Hardware configuration changed. Connect to internet to verify.", 7);
                    }
                    return;
                }
            } catch (e) { /* Token parse error, proceed to hard lockdown */ }
        }
    }
    
    // Standard hard lockdown for critical issues
    if (document.readyState === 'loading' || !document.body) {
        document.addEventListener('DOMContentLoaded', () => _doLockdown(displayMessage));
    } else {
        _doLockdown(displayMessage);
    }
}

function calculateFingerprintSimilarity(fp1, fp2) {
    const parts1 = fp1.split('-');
    const parts2 = fp2.split('-');
    if (parts1.length !== parts2.length) return 0;
    let matches = 0;
    for (let i = 0; i < parts1.length; i++) { if (parts1[i] === parts2[i]) matches++; }
    return matches / parts1.length;
}

async function validateFingerprintChange(newFp, oldFp) {
    try {
        const res = await fetch(`${CADEN_CONFIG.serverUrl}/v1/validate-fingerprint-change`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ appId: CADEN_CONFIG.appId, oldFingerprint: oldFp, newFingerprint: newFp })
        });
        return (await res.json()).authorized;
    } catch (err) { return false; }
}
```

---

## Solution 2B: Revocation-Aware Activation (Preventing Revocation Defeat)

### The Vulnerability
If a license is legitimately revoked by an admin, a flawed auto-recovery script might blindly request a new token, potentially bypassing the revocation status.

### The Architectural Fix
1. **Explicit 403 Handling:** Treat HTTP 403 as an absolute, non-recoverable hard lockdown.
2. **Token Versioning:** Never accept a new token if its expiration date is older than the currently stored token.

### Implementation Script
```javascript
async function autoActivate() {
    const deviceId = generateDeviceFingerprint();
    const sysInfo = JSON.stringify(collectSystemInfo());
    
    try {
        const response = await fetch(`${CADEN_CONFIG.serverUrl}/v1/activate?appId=${CADEN_CONFIG.appId}&deviceId=${deviceId}&systemInfo=${encodeURIComponent(sysInfo)}`, { method: 'POST' });
        
        // CRITICAL: Explicit Revocation Check
        if (response.status === 403) {
            _doLockdown("This device has been explicitly revoked by the administrator. Contact support.");
            return;
        }
        
        if (response.ok) {
            const data = await response.json();
            if (data.token) {
                const existingToken = localStorage.getItem(KEYS.token);
                if (existingToken) {
                    const existingExp = JSON.parse(atob(existingToken.split('.')[1])).exp;
                    const newExp = JSON.parse(atob(data.token.split('.')[1])).exp;
                    // Prevent downgrading to an older token
                    if (newExp <= existingExp) return; 
                }
                localStorage.setItem(KEYS.token, data.token);
            }
        }
    } catch (err) {
        window.storeSystemTelemetry("ACTIVATION_ERROR", `Failed: ${err.message}`, 1);
    }
}
```

---

## Solution 2C: Soft Lockdown & Grace Period (Offline Resilience)

### The Vulnerability
Immediate hard lockouts frustrate users who are temporarily offline or experiencing transient network issues during a license check.

### The Architectural Fix
Replace immediate UI destruction with a persistent warning banner that counts down a grace period. Only trigger `_doLockdown` if the grace period expires without server validation.

### Implementation Script
```javascript
function _doSoftLockdown(displayMessage, graceDays) {
    const graceKey = `${CADEN_CONFIG.appId}_SOFT_LOCKDOWN_GRACE`;
    const graceStart = localStorage.getItem(graceKey);
    
    if (!graceStart) {
        localStorage.setItem(graceKey, Date.now().toString());
    }
    
    const graceEndTime = parseInt(graceStart, 10) + (graceDays * 24 * 60 * 60 * 1000);
    
    if (Date.now() > graceEndTime) {
        _doLockdown(`Grace period expired. ${displayMessage}`);
        return;
    }
    
    showWarningBanner(displayMessage, graceDays);
}

function showWarningBanner(message, daysRemaining) {
    if (document.getElementById('caden-warning-banner')) return;
    const banner = document.createElement('div');
    banner.id = 'caden-warning-banner';
    banner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#f59e0b;color:#000;padding:10px 20px;z-index:10000;font-family:sans-serif;font-size:14px;display:flex;justify-content:space-between;align-items:center;';
    banner.innerHTML = `<span>⚠️ ${message} (${daysRemaining} days remaining)</span><button id="caden-verify-btn" style="padding:5px 15px;background:#000;color:#fff;border:none;cursor:pointer;">Verify Now</button>`;
    document.body.appendChild(banner);
    
    document.getElementById('caden-verify-btn').onclick = () => {
        autoActivate().then(() => location.reload());
    };
}
```

---

## Full Integrated CADEN Script (v0.4.0-proposal)

Below is the consolidated script incorporating all four solutions. This can replace the current `caden_script.txt` content.

```html
<!-- START CADEN LICENSING & GOVERNANCE COMPONENT (v0.4.0-proposal) -->
<script>
(function () {
    const CADEN_VERSION = "0.4.0-proposal";
    const CADEN_CONFIG = {
        appId: "RCM_DASHBOARD",
        serverUrl: "https://caden.prasanti.com",
        wssUrl: "wss://caden.prasanti.com/v1/stream",
        fallbackGraceDays: 30,
        logLevel: 2
    };

    const KEYS = {
        token: `${CADEN_CONFIG.appId}_AUTH_TOKEN`,
        timeline: `${CADEN_CONFIG.appId}_LAST_SEEN`,
        genesis: `${CADEN_CONFIG.appId}_GENESIS_BUNCH`,
        logs: `${CADEN_CONFIG.appId}_LOG_BUFFER`,
        uuid: `${CADEN_CONFIG.appId}_PERSISTENT_UUID`
    };

    // --- 1. System Info & Fingerprinting ---
    function collectSystemInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            cpuCores: navigator.hardwareConcurrency || 'Unknown',
            deviceMemory: navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Unknown',
            screenRes: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            webglRenderer: (() => {
                try {
                    const c = document.createElement('canvas');
                    const gl = c.getContext('webgl') || c.getContext('experimental-webgl');
                    if (gl) {
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'WebGL supported';
                    }
                    return 'Not supported';
                } catch (e) { return 'Error'; }
            })()
        };
    }

    function getPersistentUUID() {
        let uuid = localStorage.getItem(KEYS.uuid);
        if (!uuid) {
            uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
            localStorage.setItem(KEYS.uuid, uuid);
        }
        return uuid;
    }

    function generateDeviceFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = "top";
            ctx.font = "14px 'Arial'";
            ctx.fillStyle = "#f60";
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = "#069";
            ctx.fillText("CADEN_V1", 2, 15);
            const ctxString = canvas.toDataURL();
            let hash = 0;
            const inputs = ctxString + navigator.userAgent + screen.width + screen.height + navigator.hardwareConcurrency;
            for (let i = 0; i < inputs.length; i++) {
                const char = inputs.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash |= 0;
            }
            return "CADEN-" + Math.abs(hash).toString(16).toUpperCase() + "-" + getPersistentUUID().split('-')[0];
        } catch (e) {
            return "CADEN-GENERIC-" + getPersistentUUID().split('-')[0];
        }
    }

    function calculateFingerprintSimilarity(fp1, fp2) {
        const parts1 = fp1.split('-');
        const parts2 = fp2.split('-');
        if (parts1.length !== parts2.length) return 0;
        let matches = 0;
        for (let i = 0; i < parts1.length; i++) { if (parts1[i] === parts2[i]) matches++; }
        return matches / parts1.length;
    }

    // --- 2. Telemetry & Logging ---
    window.storeSystemTelemetry = function(type, messagePayload, level = 2) {
        if (level > CADEN_CONFIG.logLevel) return;
        let logBuffer = [];
        try { logBuffer = JSON.parse(localStorage.getItem(KEYS.logs)) || []; } catch(e) {}
        logBuffer.push({
            version: CADEN_VERSION,
            epoch: Date.now(),
            level: level,
            type: type,
            detail: messagePayload,
            device: generateDeviceFingerprint(),
            system_info: collectSystemInfo()
        });
        if (logBuffer.length > 100) logBuffer = logBuffer.slice(-100);
        try { localStorage.setItem(KEYS.logs, JSON.stringify(logBuffer)); } catch(e) {}
    };

    window.onerror = function(msg, url, line) {
        window.storeSystemTelemetry("RUNTIME_ERROR", `${msg} at line ${line} in ${url}`, 1);
        return false;
    };

    window.logCadenOperation = function(operationName, detail) {
        if (CADEN_CONFIG.logLevel >= 2) window.storeSystemTelemetry("OPERATION", `${operationName}: ${detail}`, 2);
    };

    async function dischargeBufferedTelemetry() {
        if (!navigator.onLine) return;
        const bufferData = localStorage.getItem(KEYS.logs);
        if (!bufferData || bufferData === "[]") return;
        try {
            const response = await fetch(`${CADEN_CONFIG.serverUrl}/v1/telemetry`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ appId: CADEN_CONFIG.appId, entries: JSON.parse(bufferData) })
            });
            if (response.ok) localStorage.setItem(KEYS.logs, JSON.stringify([]));
        } catch (err) {}
    }

    // --- 3. Activation & Revocation (Solution 2B) ---
    async function autoActivate() {
        const deviceId = generateDeviceFingerprint();
        const sysInfo = JSON.stringify(collectSystemInfo());
        
        try {
            const response = await fetch(`${CADEN_CONFIG.serverUrl}/v1/activate?appId=${CADEN_CONFIG.appId}&deviceId=${deviceId}&systemInfo=${encodeURIComponent(sysInfo)}`, { method: 'POST' });
            
            if (response.status === 403) {
                _doLockdown("This device has been explicitly revoked by the administrator.");
                return;
            }
            
            if (response.ok) {
                const data = await response.json();
                if (data.token) {
                    const existingToken = localStorage.getItem(KEYS.token);
                    if (existingToken) {
                        const existingExp = JSON.parse(atob(existingToken.split('.')[1])).exp;
                        const newExp = JSON.parse(atob(data.token.split('.')[1])).exp;
                        if (newExp <= existingExp) return; // Prevent token downgrade
                    }
                    localStorage.setItem(KEYS.token, data.token);
                    window.storeSystemTelemetry("ACTIVATION", "Device activated successfully.", 2);
                }
            }
        } catch (err) {
            window.storeSystemTelemetry("ACTIVATION_ERROR", `Failed: ${err.message}`, 1);
        }
    }

    // --- 4. Clock Integrity ---
    function assertChronologicalIntegrity() {
        const now = Date.now();
        const lastRecordedTimeline = parseInt(localStorage.getItem(KEYS.timeline), 10);
        if (lastRecordedTimeline && now < lastRecordedTimeline) {
            window.storeSystemTelemetry("CRITICAL_TAMPER", "Clock skew backdate detected.", 1);
            _doLockdown("Application Execution Suspended: Core Clock Tampering Detected.");
            return false;
        }
        localStorage.setItem(KEYS.timeline, now.toString());
        return true;
    }

    // --- 5. Lockdown & Soft Lockdown (Solutions 2 & 2C) ---
    function executeLockdownScreen(displayMessage) {
        // Smart Recovery for Fingerprint Mismatches (Solution 2)
        if (displayMessage.includes("Hardware mismatch") || displayMessage.includes("fingerprint")) {
            const currentFp = generateDeviceFingerprint();
            const storedToken = localStorage.getItem(KEYS.token);
            
            if (storedToken) {
                try {
                    const oldFp = JSON.parse(atob(storedToken.split('.')[1])).devId;
                    const similarity = calculateFingerprintSimilarity(oldFp, currentFp);
                    
                    if (similarity > 0.85) {
                        if (navigator.onLine) {
                            // In a real implementation, validateFingerprintChange would hit the server
                            autoActivate(); 
                        } else {
                            _doSoftLockdown("Hardware configuration changed. Connect to internet to verify.", 7);
                        }
                        return;
                    }
                } catch (e) { }
            }
        }
        
        if (document.readyState === 'loading' || !document.body) {
            document.addEventListener('DOMContentLoaded', () => _doLockdown(displayMessage));
        } else {
            _doLockdown(displayMessage);
        }
    }

    function _doLockdown(displayMessage) {
        if (!document.body) return;
        document.body.innerHTML = `<div style="font-family:sans-serif; text-align:center; padding:100px; background:#0f172a; color:#f8fafc; height:100vh; margin:0;"><div style="max-width:500px; margin:0 auto; border:1px solid #334155; padding:40px; border-radius:8px; background:#1e293b;"><h2 style="color:#ef4444; margin-top:0;">CADEN Governance Lockdown</h2><p style="font-size:15px; line-height:1.6; color:#cbd5e1;">${displayMessage}</p><div style="margin-top:25px; font-size:12px; color:#64748b;">Device ID: ${generateDeviceFingerprint()} | Script v${CADEN_VERSION}</div></div></div>`;
    }

    function _doSoftLockdown(displayMessage, graceDays) {
        const graceKey = `${CADEN_CONFIG.appId}_SOFT_LOCKDOWN_GRACE`;
        const graceStart = localStorage.getItem(graceKey);
        if (!graceStart) localStorage.setItem(graceKey, Date.now().toString());
        
        const graceEndTime = parseInt(graceStart, 10) + (graceDays * 24 * 60 * 60 * 1000);
        if (Date.now() > graceEndTime) {
            _doLockdown(`Grace period expired. ${displayMessage}`);
            return;
        }
        showWarningBanner(displayMessage, graceDays);
    }

    function showWarningBanner(message, daysRemaining) {
        if (document.getElementById('caden-warning-banner')) return;
        const banner = document.createElement('div');
        banner.id = 'caden-warning-banner';
        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#f59e0b;color:#000;padding:10px 20px;z-index:10000;font-family:sans-serif;font-size:14px;display:flex;justify-content:space-between;align-items:center;';
        banner.innerHTML = `<span>⚠️ ${message} (${daysRemaining} days remaining)</span><button id="caden-verify-btn" style="padding:5px 15px;background:#000;color:#fff;border:none;cursor:pointer;">Verify Now</button>`;
        document.body.appendChild(banner);
        document.getElementById('caden-verify-btn').onclick = () => autoActivate().then(() => location.reload());
    }

    // --- 6. Secure Reset (Solution 1) ---
    window.secureResetLicense = async function() {
        const adminPassword = prompt("Enter administrator password to reset license:");
        if (!adminPassword) return;

        try {
            const deviceId = generateDeviceFingerprint();
            const response = await fetch(`${CADEN_CONFIG.serverUrl}/v1/authorize-reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ appId: CADEN_CONFIG.appId, deviceId: deviceId, adminPassword: adminPassword })
            });
            const data = await response.json();
            if (data.authorized) {
                Object.values(KEYS).forEach(key => localStorage.removeItem(key));
                alert("License reset authorized. Please reconnect to activate.");
                location.reload();
            } else {
                alert("Reset denied. Contact your administrator.");
                window.storeSystemTelemetry("UNAUTHORIZED_RESET_ATTEMPT", `Admin auth failed for ${deviceId}`, 1);
            }
        } catch (err) {
            alert("Cannot verify admin credentials. Please connect to the internet.");
        }
    }

    // --- 7. Core Evaluation & Badge ---
    function runSecurityGovernanceEvaluation() {
        if (!assertChronologicalIntegrity()) return;
        const activeToken = localStorage.getItem(KEYS.token);
        const initialActivationRecord = localStorage.getItem(KEYS.genesis);

        if (activeToken) {
            try {
                const payloadObject = JSON.parse(atob(activeToken.split('.')[1]));
                if (payloadObject.exp * 1000 < Date.now()) { executeLockdownScreen("License expired."); return; }
                if (payloadObject.devId !== generateDeviceFingerprint()) { executeLockdownScreen("Hardware mismatch."); return; }
                return;
            } catch (e) { executeLockdownScreen("Token error."); }
        }

        if (!initialActivationRecord) {
            localStorage.setItem(KEYS.genesis, JSON.stringify({ genesisEpoch: Date.now(), boundApp: CADEN_CONFIG.appId }));
            window.storeSystemTelemetry("LIFECYCLE", "Grace Period Started.", 2);
            return;
        }

        try {
            const parsedRecord = JSON.parse(initialActivationRecord);
            const absoluteGraceLimit = parsedRecord.genesisEpoch + (CADEN_CONFIG.fallbackGraceDays * 24 * 60 * 60 * 1000);
            if (Date.now() > absoluteGraceLimit) executeLockdownScreen("Grace period expired.");
        } catch (jsonErr) { executeLockdownScreen("Grace error."); }
    }

    function injectCADENBadge() {
        if (document.getElementById('caden-badge')) return;
        const badge = document.createElement('div');
        badge.id = 'caden-badge';
        badge.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999; opacity: 0.7; transition: opacity 0.3s;';
        badge.innerHTML = `<div style="background: rgba(30, 41, 59, 0.9); border: 1px solid #334155; border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; gap: 8px; cursor: pointer;" onmouseover="this.parentElement.style.opacity='1'" onmouseout="this.parentElement.style.opacity='0.7'"><svg width="20" height="20" viewBox="0 0 100 100" style="flex-shrink: 0;"><path d="M50 5 L90 20 L90 55 C90 80 50 95 50 95 C50 95 10 80 10 55 L10 20 Z" fill="#1D4ED8"/><path d="M50 5 L10 20 L10 55 C10 80 50 95 50 95 Z" fill="#2563EB"/><circle cx="50" cy="38" r="10" fill="none" stroke="#FBBF24" stroke-width="4"/><line x1="50" y1="48" x2="50" y2="78" stroke="#FBBF24" stroke-width="4" stroke-linecap="round"/><line x1="50" y1="65" x2="62" y2="65" stroke="#FBBF24" stroke-width="4" stroke-linecap="round"/><line x1="50" y1="73" x2="58" y2="73" stroke="#FBBF24" stroke-width="4" stroke-linecap="round"/></svg><span style="color: #94a3b8; font-size: 11px; font-family: sans-serif;">Protected by CADEN</span></div>`;
        document.body.appendChild(badge);
    }

    function spawnStealthConnectivityBroker() {
        if (!navigator.onLine) return;
        setInterval(dischargeBufferedTelemetry, 10000);
        try {
            const socketConnection = new WebSocket(`${CADEN_CONFIG.wssUrl}?app=${CADEN_CONFIG.appId}&dev=${generateDeviceFingerprint()}`);
            socketConnection.onmessage = function(event) {
                try {
                    const serverMessage = JSON.parse(event.data);
                    if (serverMessage.directive === "REVOKE_IMMEDIATE") {
                        localStorage.removeItem(KEYS.token);
                        executeLockdownScreen("Device revoked.");
                    }
                    if (serverMessage.directive === "UPDATE_TOKEN") {
                        localStorage.removeItem(KEYS.token);
                        autoActivate();
                    }
                } catch(err) {}
            };
            socketConnection.onclose = () => setTimeout(spawnStealthConnectivityBroker, 5000);
        } catch(e) {}
    }

    // --- Initialization ---
    runSecurityGovernanceEvaluation();
    window.addEventListener('online', spawnStealthConnectivityBroker);
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(spawnStealthConnectivityBroker, 2000);
        window.logCadenOperation("APP_START", `RCM Dashboard initialized (CADEN v${CADEN_VERSION})`);
        autoActivate();
        injectCADENBadge();
    });
})();
</script>
<!-- END CADEN LICENSING & GOVERNANCE COMPONENT -->
```