#!/usr/bin/env python3
import phpserialize
import re

def php_string(content):
    length = len(content.encode('utf-8'))
    return f's:{length}:"{content}"'

# Read the actual file and check its structure
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)} chars")

# Check for common structural issues
issues = []

# 1. Check for double semicolons
if ';;' in content:
    issues.append("Double semicolons found")

# 2. Check for unmatched quotes
quote_count = content.count('"')
if quote_count % 2 != 0:
    issues.append(f"Unmatched quotes (count: {quote_count})")

# 3. Check for semicolon followed by quote without proper structure
problematic_patterns = re.findall(r';\s*"[^"]*"[^;}]', content)
if problematic_patterns:
    issues.append(f"Found {len(problematic_patterns)} problematic semicolon-quote patterns")

# 4. Check brace balance
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

if issues:
    print("❌ Structure issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ No obvious structure issues found")

# Try to find the exact location of the error by testing smaller valid chunks
print("\nTesting progressive chunks...")

# Start with just the opening
test_chunks = [
    'a:1:{s:18:"spintax-shortcodes";a:65:{}}',  # Empty structure
]

for i, chunk in enumerate(test_chunks):
    try:
        phpserialize.loads(chunk.encode('utf-8'))
        print(f"✅ Chunk {i} works: {chunk[:50]}...")
    except Exception as e:
        print(f"❌ Chunk {i} fails: {e}")

# Now let's try to build a working version step by step
print("\nBuilding structure step by step...")

# Start with the basic structure
output = 'a:1:{s:18:"spintax-shortcodes";a:65:{'

# Add just the first field
output += f's:7:"c0g3b1f";a:2:{{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{{s:6:"8q6ubd";{php_string("Test Title")};}}}}' 

# Close structure
output += '}}'

print(f"Step-by-step structure ({len(output)} chars):")
try:
    result = phpserialize.loads(output.encode('utf-8'))
    print("✅ Step-by-step structure works!")
except Exception as e:
    print(f"❌ Step-by-step structure fails: {e}")
    print("Structure:", output)
