# CADEN Offline-First Integration Guide & Architecture Feedback

This document outlines the successful architecture for integrating the CADEN licensing system with the RCM Dashboard. It serves as feedback for the CADEN team and a reference guide for future app developers.

## 1. Core Architecture: The 3-Tier Fallback
The system relies on a robust 3-tier fallback mechanism to guarantee the app works even on a first-time offline launch.

1. **Tier 1 (Online):** Loader fetches the latest script from `https://caden.prasanti.com/caden_script.txt`, caches it in `localStorage`, and runs it.
2. **Tier 2 (Offline Cache):** If offline, the loader reads the cached script from `localStorage` and runs it.
3. **Tier 3 (Cold-Start Embedded Fallback):** If offline and the cache is empty (first launch), the loader runs a minimal, hardcoded fallback script embedded directly within `caden_loader.txt`.

## 2. Strict Division of Labor
To prevent UI glitches and race conditions, responsibilities must be strictly separated:

### CADEN's Responsibility (The Gatekeeper)
*   **UI State & Auth:** Owns the registration modal, the revocation/appeal overlay, and all license validation logic.
*   **Data Persistence:** Calculates the 30-day local trial offline, saves it to `RCM_USER_INFO` in `localStorage`, and syncs with the server when online.
*   **The Handoff:** Dispatches `window.dispatchEvent(new Event('CADEN_READY'))` when auth is complete. **CADEN must not manually manipulate the app's main UI containers.**

### Dashboard's Responsibility (The App)
*   **UI Rendering:** Owns the intro video, system overview, slider, and component bindings.
*   **Data Decryption:** Handles the background decryption of `data.enc` into the global `appData` variable.
*   **The Reaction:** Listens for `CADEN_READY` and triggers its native initialization functions (e.g., `window.revealApp(true)`).

## 3. Critical Lessons Learned & Pitfalls to Avoid

### A. DOM Timing in Loaders (The "White Screen" Bug)
**Problem:** If the loader runs in the `<head>`, `document.body` is `null`. Calling `document.body.insertAdjacentHTML()` crashes the script.
**Solution:** The embedded fallback **must** wrap its DOM manipulation in `setTimeout(..., 0)` or wait for `DOMContentLoaded` to guarantee the body exists.

### B. Idempotency (The "Infinite Modal" Bug)
**Problem:** If the fallback unconditionally writes `{name: '', ...}` to `localStorage` before the user submits, a hard refresh will wipe the saved data and re-show the modal.
**Solution:** The fallback must read `localStorage` *first*. If a valid `name` and `expires_at` exist, it must skip the modal entirely and just dispatch `CADEN_READY`.

### C. Event-Driven Handoff vs. Manual DOM Manipulation
**Problem:** Manually adding CSS classes (like `.show`) to the intro overlay from the loader causes race conditions, missing buttons, and broken click handlers.
**Solution:** The loader should **only** dispatch `CADEN_READY`. The dashboard's native initialization function (e.g., `revealApp()`) must be called to ensure internal flags (like `cadenInitialized`) are set and all UI elements are properly bound.

### D. Data Race Conditions
**Problem:** Triggering the intro video before `appData` is decrypted results in "Data is not loaded" errors when the user clicks components.
**Solution:** The dashboard's `CADEN_READY` listener must poll for `window.appData` (and specifically `appData.components`) before calling `revealApp(true)`.

## 4. The Perfect Handoff Sequence
1. User opens `dashboard.html`.
2. Loader runs. If offline/cold-start, fallback shows modal.
3. User submits. Fallback saves to `localStorage` and fires `CADEN_READY`.
4. Dashboard listener hears `CADEN_READY`, waits for `appData` decryption, and calls `window.revealApp(true)`.
5. `revealApp(true)` sets internal flags, starts decryption (if not done), shows the intro video exactly once, and binds the UI.
6. When online, the loader fetches the real script, which reads the existing `localStorage` data and seamlessly syncs the exact expiry date.
