#!/usr/bin/env python3
"""
Updated fix script for 'list index out of range' bug in Graphiti MCP server.
This version tries multiple paths and provides better error reporting.
"""

import os
import re
import sys
import subprocess
from pathlib import Path

def find_graphiti_core_paths():
    """Find all possible locations of graphiti_core packages."""
    paths = []
    
    # Common virtual environment paths
    possible_venv_paths = [
        "/app/.venv/lib/python3.12/site-packages",
        "/app/.venv/lib/python3.11/site-packages", 
        "/usr/local/lib/python3.12/site-packages",
        "/usr/local/lib/python3.11/site-packages",
        "/opt/venv/lib/python3.12/site-packages",
        "/opt/venv/lib/python3.11/site-packages",
    ]
    
    for base_path in possible_venv_paths:
        graphiti_path = os.path.join(base_path, "graphiti_core", "llm_client")
        if os.path.exists(graphiti_path):
            paths.append(graphiti_path)
    
    # Try to find using pip show
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import graphiti_core; print(graphiti_core.__file__)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            package_file = result.stdout.strip()
            if package_file:
                package_dir = os.path.dirname(package_file)
                llm_client_path = os.path.join(package_dir, "llm_client")
                if os.path.exists(llm_client_path):
                    paths.append(llm_client_path)
    except Exception as e:
        print(f"Could not find package via Python import: {e}")
    
    return list(set(paths))  # Remove duplicates

def patch_file(file_path, patterns_and_replacements):
    """Apply patches to a file using regex patterns."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_content = content
    
    for pattern, replacement in patterns_and_replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original_content:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Patched: {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    else:
        print(f"No changes needed: {file_path}")
        return False

def main():
    """Main fix function with improved path detection."""
    
    # Find all possible graphiti_core paths
    graphiti_paths = find_graphiti_core_paths()
    
    if not graphiti_paths:
        print("No graphiti_core packages found!")
        print("Trying to locate using different methods...")
        
        # Try alternate search methods
        for possible_python in ["/usr/bin/python", "/usr/bin/python3", "python", "python3"]:
            try:
                result = subprocess.run([
                    possible_python, "-c", 
                    "import graphiti_core; import os; print(os.path.dirname(graphiti_core.__file__))"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    package_dir = result.stdout.strip()
                    llm_client_path = os.path.join(package_dir, "llm_client")
                    if os.path.exists(llm_client_path):
                        graphiti_paths.append(llm_client_path)
                        break
            except Exception as e:
                continue
    
    if not graphiti_paths:
        print("ERROR: Could not locate graphiti_core installation")
        return False
    
    print(f"Found graphiti_core paths: {graphiti_paths}")
    
    success_count = 0
    
    for base_path in graphiti_paths:
        print(f"\\nProcessing path: {base_path}")
        
        files_to_patch = [
            os.path.join(base_path, "openai_base_client.py"),
            os.path.join(base_path, "groq_client.py"), 
            os.path.join(base_path, "openai_generic_client.py")
        ]
        
        for file_path in files_to_patch:
            if os.path.exists(file_path):
                # Add bounds check before any response.choices[0] access
                patterns = [
                    # Pattern for response_object = response.choices[0]
                    (r'(\\s+)(response_object = response\\.choices\\[0\\])',
                     r'\\1if not response.choices:\\n\\1    raise Exception(\\'Empty response from LLM: no choices returned\\')\\n\\1\\2'),
                    # Pattern for result = response.choices[0]  
                    (r'(\\s+)(result = response\\.choices\\[0\\])',
                     r'\\1if not response.choices:\\n\\1    raise Exception(\\'Empty response from LLM: no choices returned\\')\\n\\1\\2'),
                ]
                
                if patch_file(file_path, patterns):
                    success_count += 1
            else:
                print(f"File not found: {file_path}")
    
    print(f"\\nPatching completed. {success_count} files successfully patched.")
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)