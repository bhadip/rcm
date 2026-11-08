# System Requirements & Specifications

## Functional Requirements
1. **Offline Operation**: The application must run locally without any internet dependency.
2. **Data Source**: Read data from an SME-verified Excel spreadsheet, not a live database.
3. **Data Security**: The Excel data must be converted to an AES-256 encrypted JSON format before deployment. End-users cannot view the raw calculation logic or formulas.
4. **Level 1 (Diagram)**: Display a JPG diagram with a transparent, clickable SVG overlay mapping to specific Component IDs.
5. **Level 2 (Table)**: Display a dynamic table of Failure Modes for the selected component, with status colors updating based on the global day slider.
6. **Level 3 (Charts)**: 
   - Display Reliability R(t) and Failure Rate charts.
   - X-axis for Reliability must be Logarithmic.
   - Draw a **Red dashed horizontal line** at Target R(t) and a **Red dashed vertical line** at the calculated Target Day, intersecting with a **Red 'X' marker**.
   - Draw **Yellow dashed lines** that dynamically follow the global slider's current day.

## Non-Functional Requirements
- **Tech Stack**: HTML5, CSS3, Vanilla JavaScript, CryptoJS, Chart.js.
- **Performance**: Chart updates via slider must be instantaneous (no full redraw flashing).
- **Compatibility**: Must run on modern desktop browsers (Chrome, Edge, Safari) via the `file://` protocol.
