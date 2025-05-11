#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/scripts/validate_imports.py
import os
import re
import sys

def find_python_files(directory):
    """Find all Python files in the directory and its subdirectories"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_imports(file_path):
    """Check for deprecated imports in a Python file"""
    deprecated_imports = [
        r'from\s+app\.model\b',
        r'from\s+app\.models\b',
        r'from\s+app\.controller\b',
        r'from\s+app\.controllers\b',
        r'from\s+app\.services\b',
        r'from\s+app\.blueprints\b',
        r'from\s+app\.routes\b',
        r'import\s+app\.model\b',
        r'import\s+app\.models\b',
        r'import\s+app\.controller\b',
        r'import\s+app\.controllers\b',
        r'import\s+app\.services\b',
        r'import\s+app\.blueprints\b',
        r'import\s+app\.routes\b',
        r'\bmodel\.loader\b',
    ]
    
    problems = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        for i, pattern in enumerate(deprecated_imports):
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    problems.append(f"Found deprecated import: {match}")
    
    return problems

def main():
    app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
    tests_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests')
    
    all_problems = []
    
    # Check app directory
    python_files = find_python_files(app_dir)
    for file_path in python_files:
        problems = check_imports(file_path)
        if problems:
            all_problems.append((file_path, problems))
    
    # Check tests directory
    python_files = find_python_files(tests_dir)
    for file_path in python_files:
        problems = check_imports(file_path)
        if problems:
            all_problems.append((file_path, problems))
    
    # Report problems
    if all_problems:
        print("Found deprecated imports:")
        for file_path, problems in all_problems:
            print(f"\n{os.path.relpath(file_path)}")
            for problem in problems:
                print(f"  - {problem}")
        return 1
    else:
        print("No deprecated imports found. All imports are correctly updated!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
