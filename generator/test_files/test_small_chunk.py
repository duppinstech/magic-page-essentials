#!/usr/bin/env python3
import phpserialize

# Test just the beginning structure
test_data = 'a:1:{s:18:"spintax-shortcodes";a:65:{s:7:"c0g3b1f";a:2:{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{s:6:"8q6ubd";s:89:"24/7 Emergency Roadside Assistance [location], [meta_region_code] | [xfield_company-name]";}}}}'

print(f"Testing small chunk ({len(test_data)} chars):")
print(test_data[:100] + "...")

try:
    result = phpserialize.loads(test_data.encode('utf-8'))
    print("✅ Small chunk works!")
except Exception as e:
    print(f"❌ Small chunk fails: {e}")

# Now test with the actual file, but limit to first 1000 chars
print("\nTesting first 1000 chars of actual file:")
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

chunk = content[:1000]
try:
    result = phpserialize.loads(chunk.encode('utf-8'))
    print("✅ First 1000 chars work!")
except Exception as e:
    print(f"❌ First 1000 chars fail: {e}")
    print("Content:", repr(chunk[-100:]))  # Show end of chunk
