#!/usr/bin/env python3
import phpserialize

def php_string(content):
    length = len(content.encode('utf-8'))
    return f's:{length}:"{content}"'

# Test UL content specifically
ul_content1 = "<ul class='whiterail-ul'><li>Jump Start [location], [meta_region_code]</li></ul>"
ul_content2 = "<ul class='whiterail-ul'><li>Emergency Battery Service [location], [meta_region_code]</li></ul>"

print("Testing UL content:")
print("UL 1:", repr(ul_content1))
print("UL 1 length:", len(ul_content1.encode('utf-8')))

# Build UL section
output = 'a:1:{s:18:"spintax-shortcodes";a:1:{'
output += f's:6:"feebkl";a:2:{{s:5:"label";s:11:"roadside-ul";s:7:"options";a:2:{{s:6:"9vxk2p";{php_string(ul_content1)};s:6:"rddpm7";{php_string(ul_content2)};}}}}' 
output += '}}'

print(f"\nUL structure ({len(output)} chars):")
print(output[:200] + "...")

try:
    result = phpserialize.loads(output.encode('utf-8'))
    print("✅ UL structure works!")
except Exception as e:
    print(f"❌ UL structure fails: {e}")
    
    # Check for specific issues
    print("\nDebugging:")
    print("Looking for quote issues...")
    if '";' in output:
        print("Found '; pattern")
    if '\"' in output:
        print("Found escaped quotes")
    print("Output sample:", repr(output[100:300]))
