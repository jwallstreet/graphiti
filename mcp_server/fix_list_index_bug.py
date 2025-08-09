#!/usr/bin/env python3
"""
Fix script for 'list index out of range' bug in Graphiti MCP server.
This patches the installed graphiti_core files to add proper bounds checking.
"""

import os
import re

def patch_file(file_path, patterns_and_replacements):
    """Apply patches to a file using regex patterns."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for pattern, replacement in patterns_and_replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Patched: {file_path}")
        return True
    else:
        print(f"No changes needed: {file_path}")
        return False

def main():
    base_path = "/app/.venv/lib/python3.12/site-packages/graphiti_core/llm_client"
    
    # Patch openai_base_client.py
    openai_base_patches = [
        # Fix _handle_structured_response
        (r'(\s+def _handle_structured_response.*?\n\s+""".*?"""\n)(\s+response_object = response\.choices\[0\])',
         r'\1\2if not response.choices:\n            raise Exception(\'Empty response from LLM: no choices returned\')\n        \3'),
        
        # Fix _handle_json_response  
        (r'(\s+def _handle_json_response.*?\n\s+""".*?"""\n)(\s+result = response\.choices\[0\])',
         r'\1\2if not response.choices:\n            raise Exception(\'Empty response from LLM: no choices returned\')\n        \3'),
    ]
    
    # Simpler approach - just add the check before any choices[0] access
    files_to_patch = [
        f"{base_path}/openai_base_client.py",
        f"{base_path}/groq_client.py", 
        f"{base_path}/openai_generic_client.py"
    ]
    
    for file_path in files_to_patch:
        # Add bounds check before any response.choices[0] access
        patterns = [
            (r'(\s+)(response_object = response\.choices\[0\])',
             r'\1if not response.choices:\n\1    raise Exception(\'Empty response from LLM: no choices returned\')\n\1\2'),
            (r'(\s+)(result = response\.choices\[0\])',
             r'\1if not response.choices:\n\1    raise Exception(\'Empty response from LLM: no choices returned\')\n\1\2'),
        ]
        patch_file(file_path, patterns)

if __name__ == "__main__":
    main()