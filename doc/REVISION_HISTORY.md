# Revision History

## Application Versions

### v0.5.8 (Current)
- Fixed "Â" garbage characters in footer by using HTML entities (`&copy;`, `&middot;`) and `innerHTML`.
- Ensured CADEN script has full control over UI visibility (no race conditions).

### v0.5.7
- Removed external fade-in trigger to prevent bypassing CADEN lockdown screens.

### v0.5.6
- Added anti-flash CSS (`body { opacity: 0; }`) to hide UI during license verification.

### v0.5.5
- Cleaned index.html to ensure proper CADEN script version detection and replacement.

### v0.5.4
- Integrated CADEN v0.4.0-proposal (Secure admin resets, smart fingerprint recovery, revocation awareness).

### v0.5.3
- Implemented Concept 1 "Reliability Shield" Gear Logo in header and favicon.

### v0.5.2
- Fixed smart import compatibility for System vs Component logs.

### v0.5.1
- Added Export/Import Log buttons at Level 1 (System) and Level 2 (Component).

### v0.5.0
- Added "Last Maintenance Date" column and effective day calculation logic.

### v0.4.x
- Dynamic sheet processing, consistency checks, and Excel filename arguments.

## Build Script Versions
- `build_data.py`: v0.4.5 (Strict 3-column data block validation)
- `embed_data.py`: v0.1.7 (HTML entity branding fix)
- `integrate_caden.py`: Latest (CADEN v0.3.0+ support)
