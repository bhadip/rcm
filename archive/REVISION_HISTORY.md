# Revision History

## Application Versions

### v0.5.2 (Current)
- Fixed smart import compatibility: Component-level import now correctly handles both System Logs and Component Logs.
- Added automatic detection of imported log format (nested vs flat structure).

### v0.5.1
- Added Export/Import Log buttons at Level 1 (System) and Level 2 (Component).
- System Log exports all components' maintenance dates.
- Component Log exports only the current component's dates.
- Smart merge logic: Importing a System Log at Component level extracts only the relevant component data.

### v0.5.0
- Added "Last Maintenance Date" column to Level 2 table.
- Implemented effective day calculation: `effectiveDay = sliderDay + (today - maintenanceDate)`.
- Yellow chart lines and status colors now reflect the effective day.
- Empty date assumed as today (0 offset) but not saved.
- Auto-save to browser localStorage on every date change.

### v0.4.13
- Fixed red lines stopping exactly at the blue curve intersection.
- Added red "X" marker (crossRot) at the target intersection point.
- Restored ESDV-101 hardcoded thresholds for slider color changes.

### v0.4.0
- Dynamic sheet processing: script now reads all sheets in the Excel file.
- Consistency Check A: Compares Excel sheet names vs HTML SVG component IDs.
- Consistency Check B: Verifies Failure Mode count == Target row count == Data block count.
- Detailed error reporting with row/column information on mismatch.

### v0.3.14
- Excel filename now passed as command-line argument to distinguish file versions.
- Usage: `python3 build_data.py "RCM 2.xlsx"`

### v0.3.13
- Fixed index-based mapping between Failure Modes and Target rows.
- Resolved 0.99 vs 99.0 percentage format mismatch.

### v0.3.11
- Restored hardcoded thresholds for ESDV-101 and GT-101.
- Fixed slider color changes for all components.

### v0.3.10
- Fixed Excel percentage parsing: values between 0 and 1 are now multiplied by 100.
- Resolved Target R(t) showing as 0.99% instead of 99%.

### v0.3.8
- Switched from chart-label scanning to Weibull formula calculation for Target Day.
- Formula: `t = η * (-ln(R))^(1/b)`.

### v0.2.0
- Initial Python build script (`build_data.py`).
- AES-256 encryption of Excel data to `data.enc`.
- Embed script (`embed_data.py`) to inject encrypted data into HTML.

### v0.1.0
- Initial HTML dashboard with SVG overlay.
- Basic Chart.js integration.
- Manual file upload with password decryption.

## Build Script Versions
- `build_data.py`: v0.3.14 (latest)
- `embed_data.py`: v0.1.4 (latest)

## Key Bug Fixes
1. **Log Scale Clipping (v0.4.6)**: Red lines now use `x: 1` instead of `x: 0` to prevent logarithmic scale errors.
2. **Typo Matching (v0.3.6)**: Fixed "Clossure" vs "Closure" spelling mismatch in thresholds dictionary.
3. **Header Row Detection (v0.4.4)**: Script now dynamically finds the header row instead of assuming Row 1.
4. **Read-Only Mode Crash (v0.4.2)**: Removed `read_only=True` to prevent hangs on complex Excel files.
5. **SVG Regex False Positive (v0.4.3)**: Restricted component ID search to inside `<svg>` tags only.
