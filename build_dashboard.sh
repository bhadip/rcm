#!/bin/bash

# 1. Check if an argument was provided
if [ -z "$1" ]; then
    echo "❌ Error: Missing Excel filename."
    echo "Usage: ./build_dashboard.sh \"RCM 5.xlsx\""
    exit 1
fi

EXCEL_FILE="$1"

# 2. Check if the file actually exists
if [ ! -f "$EXCEL_FILE" ]; then
    echo "❌ Error: File '$EXCEL_FILE' not found in the current directory."
    exit 1
fi

echo "🚀 Starting build for $EXCEL_FILE..."

# 3. Run the 4-step pipeline
python3 build_data.py "$EXCEL_FILE"
python3 generate_complete.py
python3 integrate_caden.py
python3 embed_data.py "$EXCEL_FILE"

echo "✅ Build complete! Check dashboard.html"
