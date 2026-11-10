# System Requirements & Specifications

## Functional Requirements
1. **Offline Operation**: The application must run locally without any internet dependency.
2. **Data Security**: The Excel data must be converted to an AES-256 encrypted JSON format before deployment.
3. **CADEN Governance**: Must enforce hardware binding, clock integrity, and remote revocation capabilities.
4. **Level 1 (Diagram)**: Display a JPG diagram with a transparent, clickable SVG overlay.
5. **Level 2 (Table)**: Display dynamic Failure Modes with a "Last Maintenance Date" column.
6. **Level 3 (Charts)**: Logarithmic reliability charts with dynamic target intersection markers (Red crosshairs) and current day indicators (Yellow dashed lines).

## Non-Functional Requirements
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, CryptoJS, Chart.js, Python 3.x.
- **Performance**: Chart updates via slider must be instantaneous.
- **Compatibility**: Must run on modern desktop browsers via the `file://` protocol.
