#!/usr/bin/env python3

# Test UL content length
test_ul = '<ul class="whiterail-ul"><li>Jump Start [location], [meta_region_code]</li><li>Emergency Battery Service [location], [meta_region_code]</li></ul>'
print(f'UL content length: {len(test_ul)} chars')
print(f'UL content UTF-8 bytes: {len(test_ul.encode("utf-8"))} bytes')

# Check what's in our output file
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the UL string length declarations
import re
ul_matches = re.findall(r's:(\d+):"<ul[^"]*>', content)
print(f'Found UL string lengths in file: {ul_matches}')

# Find the actual UL content
ul_content_matches = re.findall(r's:\d+:"(<ul class="whiterail-ul">.*?</ul>)"', content, re.DOTALL)
if ul_content_matches:
    actual_ul = ul_content_matches[0]
    actual_length = len(actual_ul.encode('utf-8'))
    print(f'Actual UL content length: {actual_length} bytes')
    print(f'Actual UL content preview: {actual_ul[:100]}...')
else:
    print('No UL content found in regex search')
