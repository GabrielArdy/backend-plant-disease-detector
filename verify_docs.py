#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/verify_docs.py

"""
Quick script to verify our documentation updates
"""

import re
import sys
from pathlib import Path

def check_file_contains_text(file_path, search_text):
    """Check if a file contains specific text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return search_text in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def verify_documentation():
    """Verify that our documentation has been updated with the fixes"""
    docs_path = Path(__file__).parent
    
    # Files to check
    files = {
        "README.md": [
            "Recent Updates (May 15, 2025)",
            "Fixed GridFS Storage Issue",
            "Enhanced Advice Generation",
            "Added Health Monitoring",
        ],
        "docs/gridfs_storage.md": [
            "GridFS Initialization (Updated May 15, 2025)",
            "GridFSProxy class",
        ],
        "docs/ai_advice.md": [
            "Fallback Mechanism (Enhanced May 15, 2025)",
            "Robust Response Parsing",
        ]
    }
    
    success = True
    
    for file, texts in files.items():
        file_path = docs_path / file
        print(f"\nChecking {file}...")
        
        if not file_path.exists():
            print(f"  ❌ File not found: {file}")
            success = False
            continue
        
        for text in texts:
            if check_file_contains_text(file_path, text):
                print(f"  ✅ Found: '{text}'")
            else:
                print(f"  ❌ Missing: '{text}'")
                success = False
    
    return success

if __name__ == "__main__":
    print("Verifying documentation updates...")
    if verify_documentation():
        print("\n✅ Documentation successfully updated with all the required information.")
        sys.exit(0)
    else:
        print("\n❌ Documentation update incomplete. Please check the messages above.")
        sys.exit(1)
