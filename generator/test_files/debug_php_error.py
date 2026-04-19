#!/usr/bin/env python3
import phpserialize
import re

try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Convert to string for analysis
    content_str = data.decode('utf-8')
    
    # Look for potential issues in the structure
    print("Analyzing structure...")
    
    # Find all s:LENGTH:"STRING" patterns
    string_patterns = re.findall(r's:(\d+):"([^"]*)"', content_str)
    print(f"Found {len(string_patterns)} string patterns")
    
    # Check for length mismatches
    mismatches = []
    for i, (length_str, string_content) in enumerate(string_patterns[:10]):  # Check first 10
        declared_length = int(length_str)
        actual_length = len(string_content.encode('utf-8'))
        if declared_length != actual_length:
            mismatches.append((i, declared_length, actual_length, string_content[:50]))
    
    if mismatches:
        print(f"❌ Found {len(mismatches)} length mismatches:")
        for i, declared, actual, content_preview in mismatches:
            print(f"  Pattern {i}: declared={declared}, actual={actual}, content='{content_preview}...'")
    else:
        print("✅ All string lengths match (in first 10 patterns)")
    
    # Look for problematic patterns
    if ';"' in content_str:
        count = content_str.count(';"')
        print(f"Found {count} instances of ';\"' which might be problematic")
    
    # Test PHP deserialization
    result = phpserialize.loads(data)
    print("✅ PHP deserialization successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Try to find where the error occurs by testing chunks
    if 'data' in locals():
        print("Testing chunks to isolate error...")
        content_str = data.decode('utf-8')
        
        # Find the first problematic area
        for i in range(0, len(content_str), 1000):
            chunk = content_str[:i+1000]
            try:
                phpserialize.loads(chunk.encode('utf-8'))
            except:
                print(f"Error occurs around character {i}-{i+1000}")
                print(f"Problematic area: ...{chunk[max(0,i-50):i+100]}...")
                break
