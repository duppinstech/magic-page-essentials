#!/usr/bin/env python3
"""
Detailed comparison of the actual files to find the exact issue
"""

import re

def analyze_php_serialization(content, name):
    """Analyze PHP serialization for common issues"""
    print(f"\n=== ANALYZING {name} ===")
    
    # Check for basic structure
    if content.startswith('a:1:{s:18:"spintax-shortcodes";a:65:{'):
        print("✅ Correct opening structure")
    else:
        print("❌ Incorrect opening structure")
        print(f"Starts with: {content[:50]}")
    
    # Check for proper closing
    if content.endswith('}}'):
        print("✅ Correct closing structure")
    else:
        print("❌ Incorrect closing structure")
        print(f"Ends with: {content[-50:]}")
    
    # Count braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    print(f"Open braces: {open_braces}")
    print(f"Close braces: {close_braces}")
    if open_braces == close_braces:
        print("✅ Braces balanced")
    else:
        print("❌ Braces NOT balanced")
    
    # Count semicolons
    semicolons = content.count(';')
    print(f"Semicolons: {semicolons}")
    
    # Check string length accuracy
    string_errors = []
    for match in re.finditer(r's:(\d+):"([^"]*)"', content):
        declared_length = int(match.group(1))
        actual_content = match.group(2)
        actual_length = len(actual_content.encode('utf-8'))
        
        if declared_length != actual_length:
            string_errors.append({
                'declared': declared_length,
                'actual': actual_length,
                'content': actual_content[:50] + '...' if len(actual_content) > 50 else actual_content
            })
    
    if string_errors:
        print(f"❌ Found {len(string_errors)} string length errors:")
        for i, error in enumerate(string_errors[:5]):  # Show first 5 errors
            print(f"  {i+1}. Declared: {error['declared']}, Actual: {error['actual']}")
            print(f"     Content: {error['content']}")
    else:
        print("✅ All string lengths are correct")
    
    # Check array count accuracy
    array_errors = []
    # This is more complex, but let's check the main array
    main_match = re.search(r'a:65:\{(.+)\}$', content)
    if main_match:
        # Count top-level field entries
        field_pattern = r's:\d+:"[^"]+";a:2:\{s:5:"label";s:\d+:"[^"]+";s:7:"options";a:\d+:\{[^}]+\}\}'
        field_matches = re.findall(field_pattern, content)
        actual_fields = len(field_matches)
        print(f"Declared fields: 65")
        print(f"Actual fields found: {actual_fields}")
        
        if actual_fields != 65:
            print("❌ Field count mismatch")
        else:
            print("✅ Field count matches")

def main():
    # Analyze working sample
    with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
        sample_content = f.read()
    
    analyze_php_serialization(sample_content, "WORKING SAMPLE")
    
    # Analyze current output
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    analyze_php_serialization(current_content, "CURRENT OUTPUT")
    
    # Direct byte comparison
    print(f"\n=== DIRECT COMPARISON ===")
    print(f"Sample size: {len(sample_content)} characters")
    print(f"Current size: {len(current_content)} characters")
    
    if sample_content == current_content:
        print("✅ Files are IDENTICAL!")
    else:
        print("❌ Files are DIFFERENT!")
        
        # Find first difference
        for i, (s, c) in enumerate(zip(sample_content, current_content)):
            if s != c:
                start = max(0, i-50)
                end = min(len(sample_content), i+50)
                print(f"\nFirst difference at position {i}:")
                print(f"Sample char:  '{s}' (ord: {ord(s)})")
                print(f"Current char: '{c}' (ord: {ord(c)})")
                print(f"Context sample:  ...{repr(sample_content[start:end])}...")
                print(f"Context current: ...{repr(current_content[start:end])}...")
                break
        
        # Check if one is longer
        if len(sample_content) != len(current_content):
            shorter = min(len(sample_content), len(current_content))
            print(f"\nLength difference at position {shorter}:")
            if len(sample_content) > len(current_content):
                print(f"Sample continues: {repr(sample_content[shorter:shorter+50])}")
            else:
                print(f"Current continues: {repr(current_content[shorter:shorter+50])}")

if __name__ == "__main__":
    main()
