import os
import shutil
import zipfile
import subprocess

def publish_release():
    print("🚀 Starting Release & Demo Publication Workflow...\n")
    
    # ==========================================
    # STEP 1: Create the ZIP Installer
    # ==========================================
    zip_name = "RCM_Dashboard_Installer.zip"
    source_files = {
        "dashboard.html": "dashboard.html",
        "chart.umd.js": "chart.umd.js",          # FIXED: Correct filename
        "crypto-js.min.js": "crypto-js.min.js",
        "intro.mp4": "intro.mp4"
    }
    
    if os.path.exists(zip_name):
        os.remove(zip_name)

    print("📦 Step 1: Building RCM Dashboard Installer...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for target_name, source_path in source_files.items():
            if os.path.exists(source_path):
                zf.write(source_path, target_name)
                print(f"  ✅ Added {target_name}")
            else:
                print(f"  ⚠️  Warning: {source_path} not found!")

        if os.path.exists("equipments"):
            for root, dirs, files in os.walk("equipments"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=".")
                    zf.write(file_path, arcname)
            print(f"  ✅ Added equipments/ folder")
        
        # Launch scripts and README
        zf.writestr("Launch.bat", '@echo off\r\necho Launching RCM Dashboard...\r\nstart "" "%~dp0dashboard.html"\r\nexit\r\n')
        zf.writestr("Launch.command", '#!/bin/bash\nDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"\nchmod +x "$DIR/Launch.command"\nopen "$DIR/dashboard.html"\n')
        zf.writestr("README.txt", "1. Double-click Launch.bat (Windows) or Launch.command (Mac).\n2. Fill out the 30-day offline trial registration.\n3. Enjoy the RCM Dashboard!")
        print("  ✅ Added launch scripts and README")
    print(f"🚀 Success! Created {zip_name}\n")

    # ==========================================
    # STEP 2: Prepare Web Demo Folder
    # ==========================================
    print("🌐 Step 2: Preparing GitHub Pages Web Demo...")
    demo_dir = "docs" # GitHub Pages natively serves from 'docs'
    
    # Clean and recreate demo directory
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    os.makedirs(demo_dir)

    # Copy demo files
    demo_files = ["dashboard.html", "chart.umd.js", "crypto-js.min.js", "intro.mp4", "user_guide.html"]
    for f in demo_files:
        if os.path.exists(f):
            shutil.copy(f, os.path.join(demo_dir, f))
            print(f"  ✅ Copied {f} to {demo_dir}/")
    
    if os.path.exists("equipments"):
        shutil.copytree("equipments", os.path.join(demo_dir, "equipments"))
        print(f"  ✅ Copied equipments/ to {demo_dir}/")

    # Copy the ZIP installer into the demo folder so visitors can download it
    shutil.copy(zip_name, os.path.join(demo_dir, zip_name))
    print(f"  ✅ Copied {zip_name} to {demo_dir}/ for visitor download\n")

    # ==========================================
    # STEP 3: Create Demo Landing Page
    # ==========================================
    print("📄 Step 3: Creating Demo Landing Page...")
    landing_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCM Dashboard - Live Demo & Download</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; text-align: center; padding: 20px; }}
        h1 {{ color: #3b82f6; font-size: 2.5rem; margin-bottom: 10px; }}
        p {{ color: #cbd5e1; font-size: 1.2rem; max-width: 600px; margin-bottom: 30px; }}
        .btn {{ display: inline-block; padding: 15px 30px; margin: 10px; font-size: 1.1rem; font-weight: bold; text-decoration: none; border-radius: 8px; transition: transform 0.2s, background 0.2s; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn-demo {{ background: #3b82f6; color: white; }}
        .btn-demo:hover {{ background: #2563eb; }}
        .btn-download {{ background: #10b981; color: white; }}
        .btn-download:hover {{ background: #059669; }}
        .btn-guide {{ background: #8b5cf6; color: white; }}
        .btn-guide:hover {{ background: #7c3aed; }}
        .note {{ margin-top: 40px; font-size: 0.9rem; color: #64748b; max-width: 500px; line-height: 1.5; }}
    </style>
</head>
<body>
    <h1>RCM Reliability Dashboard</h1>
    <p>Experience the offline-first Reliability Centered Maintenance dashboard. Register for a 30-day local trial and explore component failure modes, time-travel analysis, and maintenance tracking.</p>
    
    <div>
        <a href="dashboard.html" class="btn btn-demo">🚀 Try Live Demo</a>
        <a href="user_guide.html" class="btn btn-guide">📖 User Guide</a>
        <a href="{zip_name}" class="btn btn-download" download>⬇️ Download Offline Installer</a>
    </div>

    <div class="note">
        <strong>Note:</strong> The Live Demo runs entirely in your browser. For a true offline experience, download the Installer ZIP, extract it, and run <code>Launch.bat</code> (Windows) or <code>Launch.command</code> (Mac).
    </div>
</body>
</html>"""
    
    with open(os.path.join(demo_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(landing_page)
    print("  ✅ Created docs/index.html landing page\n")

    # ==========================================
    # STEP 4: Git Commit and Push
    # ==========================================
    print("📤 Step 4: Committing and Pushing to GitHub...")
    
    commands = [
        "git add -A",
        f'git commit -m "Release: Build installer ZIP and update GitHub Pages demo"',
        "git push origin main"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Success: {result.stdout.strip()}")
        else:
            print(f"  ❌ Error: {result.stderr.strip()}")
            
    print("\n🎉 Release Published Successfully!")
    print("👉 Next: Go to your GitHub Repo -> Settings -> Pages -> Set 'Source' to 'Deploy from a branch' -> 'main' branch -> '/docs' folder -> Save.")

if __name__ == "__main__":
    publish_release()
