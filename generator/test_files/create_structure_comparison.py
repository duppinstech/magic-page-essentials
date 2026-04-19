#!/usr/bin/env python3
"""
Create structure comparison files by removing content and keeping only PHP serialization structure
"""

import re

def strip_content_keep_structure(content):
    """Remove all content but keep PHP serialization structure intact"""
    
    # Replace all string content with placeholder, but keep the structure
    # Pattern: s:123:"any content here" -> s:X:"CONTENT"
    
    def replace_string_content(match):
        length = match.group(1)
        # Keep the structure but replace content with placeholder
        return f's:X:"CONTENT"'
    
    # Replace all string declarations but keep structure
    result = re.sub(r's:(\d+):"[^"]*"', replace_string_content, content)
    
    # Also replace array counts with placeholder for easier comparison
    # a:123:{ -> a:X:{
    result = re.sub(r'a:(\d+):', 'a:X:', result)
    
    return result

def main():
    # Process the working sample
    print("Processing working sample...")
    with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
        sample_content = f.read()
    
    sample_structure = strip_content_keep_structure(sample_content)
    
    with open('magicpage_template_structure.txt', 'w', encoding='utf-8') as f:
        f.write(sample_structure)
    print("Created: magicpage_template_structure.txt")
    
    # Process the current output
    print("Processing current output...")
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    current_structure = strip_content_keep_structure(current_content)
    
    with open('magicpage_current_structure.txt', 'w', encoding='utf-8') as f:
        f.write(current_structure)
    print("Created: magicpage_current_structure.txt")
    
    # Basic comparison
    print("\n=== BASIC COMPARISON ===")
    print(f"Sample structure length: {len(sample_structure)}")
    print(f"Current structure length: {len(current_structure)}")
    
    if sample_structure == current_structure:
        print("✅ Structures are IDENTICAL!")
    else:
        print("❌ Structures are DIFFERENT!")
        
        # Find first difference
        for i, (s, c) in enumerate(zip(sample_structure, current_structure)):
            if s != c:
                start = max(0, i-20)
                end = min(len(sample_structure), i+20)
                print(f"\nFirst difference at position {i}:")
                print(f"Sample:  ...{sample_structure[start:end]}...")
                print(f"Current: ...{current_structure[start:end]}...")
                break

if __name__ == "__main__":
    main()
