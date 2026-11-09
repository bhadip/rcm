# Architecture & Design

## System Overview
The system uses a **Build-Time Encryption / Run-Time Decryption** architecture to protect SME intellectual property while maintaining a zero-dependency frontend.

## Data Flow
1. **Source**: SME updates `RCM 1-2.xlsx` (or similar) with Failure Modes, Weibull parameters (b, η), and Target thresholds.
2. **Build Phase (`build_data.py`)**:
   - Dynamically detects all sheets (components) in the workbook.
   - Performs consistency checks:
     - Component count in Excel vs HTML SVG overlay IDs.
     - Failure Mode count vs Target row count per sheet.
     - Failure Mode count vs 3-column data block count.
   - Extracts metadata and time-series arrays from each sheet.
   - Calculates exact Target Days using the Weibull formula: `t = η * (-ln(R))^(1/b)`.
   - Encrypts the resulting JSON payload using AES-256-CBC via `pycryptodome`.
3. **Embed Phase (`embed_data.py`)**:
   - Injects the Base64-encoded encrypted string and obfuscated password directly into `index.html`.
   - Outputs a single, portable `dashboard.html` file.
4. **Run Phase (`dashboard.html`)**:
   - On load, the browser uses `crypto-js.min.js` to decrypt the embedded string in memory using the obfuscated password.
   - Vanilla JS renders the SVG overlay and binds click events.
   - Chart.js renders the curves. Slider movements only update specific dataset coordinates (`chart.update('none')`) to prevent UI flashing.

## Security Model
- **At Rest**: Data is AES-256 encrypted.
- **In Transit**: N/A (Offline).
- **In Memory**: Decrypted only in the browser's JavaScript runtime. The password is Base64 obfuscated in the source code to prevent casual viewing.
- **Maintenance Logs**: Stored in browser localStorage with optional export/import as JSON files.

## Component Mapping
- Each Excel sheet name must match an SVG component ID in `index.html`.
- SVG overlay uses `preserveAspectRatio="none"` to scale with the background JPG.
- Clickable areas are defined as `<rect>` elements with `class="clickable-area"`.
