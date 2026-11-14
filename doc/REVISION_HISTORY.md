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

## 🎨 Chart Style Archive (Pre-v0.7.0)
*Use this reference if reverting to the Light Theme is required.*
- **Background:** White (`#ffffff`)
- **Border:** None
- **Grid:** Light Gray (`#eee`)
- **Typography:** Dark Gray (`#333`), Standard sans-serif.
- **Data Series:**
  - Reliability Curve: Blue (`#3498db`), solid, 2px.
  - Ongoing/Alarm: Yellow/Red dashed lines, no specific point markers at intersections (used simple line segments).
  - Actual Data: White circles with black border.
- **Legend:** Hidden (`display: false`).


### v0.7.10
- **Custom HTML Legend (Reliability chart):** Replaced Chart.js canvas legend (which rendered dashed *boxes*) with a hand-built HTML legend under the chart — solid blue line (Reliability Curve), dashed yellow line (Ongoing), dashed red line (Alarm), small white circle (Failure event, shown only when actual data exists).
- **Failure Rate chart:** Legend removed entirely.
- **Chart sizing:** Canvas wrapped in a flex `chart-canvas-wrap` so charts fill their quadrant correctly.

### v0.7.0–v0.7.9 (Dark Engineering Theme)
- Pure-black chart background, dark-gray grid, white typography; bold titles.
- Reliability Y-axis max = 105%; X-axis logarithmic; Failure Rate X-axis linear.
- Ongoing = yellow dashed L-line + yellow diamond at intersection; Alarm = bright-red dashed L-line + red cross at intersection; Failure events = small white circles on the curve.
- Conditional red chart border when a Failure Mode has actual failure-event data.
- Intersection markers move correctly with the slider (separated line vs. marker datasets).
