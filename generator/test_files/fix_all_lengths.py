#!/usr/bin/env python3
"""
Fix ALL string length calculations in the current output to match actual byte lengths
"""

import re

def fix_string_lengths(content):
    """Fix all s:LENGTH:"content" declarations to use correct byte lengths"""
    
    def replace_length(match):
        declared_length = match.group(1)
        content_str = match.group(2)
        actual_length = len(content_str.encode('utf-8'))
        
        # Return corrected length
        return f's:{actual_length}:"{content_str}"'
    
    # Replace all string length declarations
    fixed_content = re.sub(r's:(\d+):"([^"]*)"', replace_length, content)
    
    return fixed_content

def main():
    # Load current output
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    print("Fixing all string length calculations...")
    
    # Fix all lengths
    fixed_content = fix_string_lengths(current_content)
    
    # Save fixed version
    with open('magicpage_import_fixed_lengths.txt', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Created: magicpage_import_fixed_lengths.txt")
    
    # Verify the fix
    print("\n=== VERIFICATION ===")
    length_errors = 0
    for match in re.finditer(r's:(\d+):"([^"]*)"', fixed_content):
        declared_length = int(match.group(1))
        actual_content = match.group(2)
        actual_length = len(actual_content.encode('utf-8'))
        
        if declared_length != actual_length:
            length_errors += 1
            if length_errors <= 3:  # Show first 3 errors
                print(f"❌ Length error: declared {declared_length}, actual {actual_length}")
                print(f"   Content: {actual_content[:50]}...")
    
    if length_errors == 0:
        print("✅ All string lengths are now correct!")
    else:
        print(f"❌ Still found {length_errors} length errors")

if __name__ == "__main__":
    main()
