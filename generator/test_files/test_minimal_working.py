#!/usr/bin/env python3
import phpserialize

# Create a minimal working version with just one field
def php_string(content):
    length = len(content.encode('utf-8'))
    return f's:{length}:"{content}"'

# Build minimal structure
output = 'a:1:{s:18:"spintax-shortcodes";a:1:{'
output += f's:7:"c0g3b1f";a:2:{{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{{s:6:"8q6ubd";{php_string("Test Title")};}}}}' 
output += '}}'

print(f"Minimal structure ({len(output)} chars):")
print(output)

try:
    result = phpserialize.loads(output.encode('utf-8'))
    print("✅ Minimal structure works!")
    print("Result:", result)
except Exception as e:
    print(f"❌ Minimal structure fails: {e}")

# Now let's check the actual file's ending
print("\nChecking actual file ending:")
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)}")
print("Last 100 characters:", repr(content[-100:]))

# Check if file ends properly
if content.endswith('}}'):
    print("✅ File ends with proper closing braces")
else:
    print("❌ File doesn't end with proper closing braces")
