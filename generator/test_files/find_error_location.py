#!/usr/bin/env python3
import phpserialize

def test_chunk(data, start, end):
    """Test if a chunk of data is valid PHP serialization"""
    chunk = data[start:end]
    try:
        phpserialize.loads(chunk)
        return True
    except:
        return False

# Read the file
with open('magicpage_import_from_txt.txt', 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")

# The issue is that the file is incomplete when we test chunks
# Let's try to find where the structure becomes invalid
# by testing if we can at least parse the beginning correctly

content_str = data.decode('utf-8')

# Look for the exact error by examining the structure
# Let's manually check the first few fields
print("Examining first few fields...")

# Extract just the first field to test
import re
first_field_match = re.search(r'(a:1:\{s:18:"spintax-shortcodes";a:65:\{s:7:"c0g3b1f";a:2:\{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:\{s:6:"8q6ubd";s:89:"[^"]*";\}\}\})', content_str)

if first_field_match:
    first_field = first_field_match.group(1) + '}}'  # Close the structure
    print(f"First field structure ({len(first_field)} chars):")
    print(first_field)
    
    try:
        result = phpserialize.loads(first_field.encode('utf-8'))
        print("✅ First field works!")
    except Exception as e:
        print(f"❌ First field fails: {e}")
else:
    print("Could not extract first field")

# Let's also check if there are any non-ASCII characters that might cause issues
print("\nChecking for problematic characters...")
for i, char in enumerate(content_str[:1000]):
    if ord(char) > 127:
        print(f"Non-ASCII character at position {i}: {repr(char)} (ord: {ord(char)})")
        break
else:
    print("No non-ASCII characters in first 1000 chars")
