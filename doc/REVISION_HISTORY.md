# Revision History

## Application Versions

### v0.6.15 (Current)
- **CADEN Polling Fallback:** Added robust fallback to read license expiry from `RCM_GENESIS_BUNCH` + `RCM_SERVER_TRIAL_DAYS` when JWT tokens are absent.
- **Footer Layout:** Moved User Name and License Expiry to a clean 3-column footer (Left: User, Center: Branding, Right: License).
- **UI Cleanup:** Removed stray "LICENSE EXPIRES" text from the header area.

### v0.6.12
- **Dynamic Metadata:** `build_data.py` now writes `build_info.json` to track the real Excel filename and script version for the build pipeline.

### v0.6.10
- **License Chip Visibility:** Made the User/License chip visible by default (showing `—` placeholders) and raised its `z-index` to sit cleanly above the CADEN badge.

### v0.6.9
- **Zero-Touch Startup:** Completely removed the "Secure Data Access" login modal. Embedded data now auto-decrypts and loads on startup.
- **Calibration Shortcut:** Removed the visible "Calibrate SVG" button; calibration mode is now toggled exclusively via `Ctrl/Cmd + Shift + L`.
- **Maintenance Controls:** Added "Clear All Maintenance" (Level 1) and "Clear Component Maintenance" (Level 2) buttons.
- **Table Improvements:** Right-aligned sequence numbers; added a blue dot indicator for Failure Modes containing actual historical data.

### v0.6.0
- **New Excel Layout Support:** Rewrote `build_data.py` parser to handle the new vertical-band layout (Parameter Grafik, Target blocks, and Actual Data blocks).
- **Dynamic Chart Axes:** Reliability chart Y-min and X-max now dynamically read from the Excel "Parameter Grafik" block.
- **Actual Data Plotting:** Historical failure events are now plotted as white circles on the Reliability chart.
- **Strict Validation:** Build aborts if `targetDay` or time-series data is missing for any Failure Mode.

## Build Script Versions
- `build_data.py`: v0.6.12 (Writes `build_info.json`, strict consistency checks)
- `embed_data.py`: v0.2.1 (Injects dynamic `APP_BUILD_META`, no hardcoded placeholders)
- `integrate_caden.py`: Latest (CADEN v0.6.4+ support)
