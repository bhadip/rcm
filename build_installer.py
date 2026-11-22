import os
import shutil
import zipfile

def build_installer():
    zip_name = "RCM_Dashboard_Installer.zip"
    source_files = {
        "dashboard.html": "dashboard.html",
        "chart.min.js": "chart.min.js",
        "crypto-js.min.js": "crypto-js.min.js",
        "intro.mp4": "intro.mp4"
    }
    
    # Clean up previous build
    if os.path.exists(zip_name):
        os.remove(zip_name)

    print("📦 Building RCM Dashboard Installer...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Add core files
        for target_name, source_path in source_files.items():
            if os.path.exists(source_path):
                zf.write(source_path, target_name)
                print(f"  ✅ Added {target_name}")
            else:
                print(f"  ⚠️  Warning: {source_path} not found!")

        # 2. Add equipments folder
        if os.path.exists("equipments"):
            for root, dirs, files in os.walk("equipments"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=".")
                    zf.write(file_path, arcname)
            print(f"  ✅ Added equipments/ folder")
        else:
            print(f"  ⚠️  Warning: equipments/ folder not found!")

        # 3. Generate and add Launch.bat (Windows)
        bat_content = '@echo off\r\necho Launching RCM Dashboard...\r\nstart "" "%~dp0dashboard.html"\r\nexit\r\n'
        zf.writestr("Launch.bat", bat_content)
        print("  ✅ Added Launch.bat")

        # 4. Generate and add Launch.command (Mac/Linux)
        cmd_content = '#!/bin/bash\nDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"\nopen "$DIR/dashboard.html"\n'
        zf.writestr("Launch.command", cmd_content)
        print("  ✅ Added Launch.command")

        # 5. Generate and add README.txt
        readme = """RCM Reliability Dashboard - User Guide
=====================================

1. HOW TO LAUNCH:
   - Windows: Double-click "Launch.bat"
   - Mac: Double-click "Launch.command" (or right-click -> Open)
   - Alternatively, just open "dashboard.html" in your web browser.

2. FIRST TIME SETUP:
   - The app works 100% offline.
   - On first launch, fill out the Registration Form to activate your 30-day local trial.
   - Click "Start" to watch the intro video, or "Skip Intro" to go straight to the dashboard.

3. NAVIGATION:
   - Click any equipment on the diagram (e.g., ESDV-101) to view its Failure Modes.
   - Use the "Current Day" slider at the bottom to see how failure modes change over time.
   - Use the top-right menu to Export/Import System Logs.

4. SUPPORT:
   - If your license expires, the app will continue to work, but the footer will show a red warning.
   - Contact your administrator for license renewal.
"""
        zf.writestr("README.txt", readme)
        print("  ✅ Added README.txt")

    print(f"\n🚀 Success! Created {zip_name}")

if __name__ == "__main__":
    build_installer()
