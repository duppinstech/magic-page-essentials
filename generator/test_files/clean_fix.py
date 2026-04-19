#!/usr/bin/env python3
import re

# Start with the working sample
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("Starting with working sample...")

# Replace only H1 content (simple replacement)
h1_pattern = r's:\d+:"<h1>[^<]*</h1>"'
h1_replacement = 's:64:"<h1>24/7 Roadside Assistance [location], [meta_region_code]</h1>"'
content = re.sub(h1_pattern, h1_replacement, content, count=1)
print("✅ Replaced H1 content")

# Replace UL content with our raw content
ul_content = '<ul class="whiterail-ul"><li>Jump Start [location], [meta_region_code]</li><li>Emergency Battery Service [location], [meta_region_code]</li><li>Battery Boost Service [location], [meta_region_code]</li><li>Flat Tire Change [location], [meta_region_code]</li><li>Fuel Delivery Near Me [location], [meta_region_code]</li><li>Gas Delivery Service [location], [meta_region_code]</li><li>Out of Gas Fuel Delivery [location], [meta_region_code]</li><li>Winch-out Service [location], [meta_region_code]</li><li>Ditch Pull-Outs [location], [meta_region_code]</li><li>Locked out of Car Service [location], [meta_region_code]</li><li>Vehicle Lockout Service [location], [meta_region_code]</li><li>Light Duty Towing [location], [meta_region_code]</li><li>Medium Duty Towing [location], [meta_region_code]</li><li>Heavy Duty Towing [location], [meta_region_code]</li><li>Truck Roadside Service [location], [meta_region_code]</li><li>Towing [location], [meta_region_code]</li></ul>'

ul_length = len(ul_content.encode('utf-8'))

# Replace ALL UL content carefully
ul_pattern = r's:\d+:"<ul class="whiterail-ul">.*?</ul>"'
ul_replacement = f's:{ul_length}:"{ul_content}"'
content = re.sub(ul_pattern, ul_replacement, content, flags=re.DOTALL)
print(f"✅ Replaced UL content ({ul_length} bytes)")

# Write the clean version
with open('magicpage_import_from_txt_CLEAN.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Created: magicpage_import_from_txt_CLEAN.txt")

# Test it
import phpserialize
try:
    with open('magicpage_import_from_txt_CLEAN.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! Clean file passes PHP serialization!')
except Exception as e:
    print(f'❌ Clean file error: {e}')
    
# Quick structure check
clean_open = content.count('{')
clean_close = content.count('}')
clean_semi = content.count(';')
print(f"Clean file structure: {{ {clean_open}, }} {clean_close}, ; {clean_semi}")
