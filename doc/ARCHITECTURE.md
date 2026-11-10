# Architecture & Design

## System Overview
The system uses a **Build-Time Encryption / Run-Time Decryption** architecture combined with **CADEN Client-Side Governance**.

## Data Flow
1. **Source**: SME updates `RCM 2.xlsx` with Failure Modes, Weibull parameters, and Target thresholds.
2. **Build Phase**: `build_data.py` dynamically parses sheets, validates consistency (FM count == Target count == Data blocks), and encrypts the JSON payload using AES-256-CBC.
3. **Embed Phase**: `embed_data.py` injects the encrypted string into `index.html`.
4. **Run Phase**: `dashboard.html` decrypts the data in memory. CADEN script verifies hardware fingerprint and license status before revealing the UI (`opacity: 1`).

## Security Model
- **At Rest**: Data is AES-256 encrypted.
- **In Memory**: Decrypted only in the browser's JavaScript runtime.
- **CADEN Governance**: Uses persistent UUIDs, canvas fingerprinting, and stealth WebSocket agents for remote revocation.
