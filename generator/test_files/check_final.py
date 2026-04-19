#!/usr/bin/env python3
import re

with open('magicpage_import_from_txt_FINAL.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Find UL content
ul_match = re.search(r's:(\d+):"(<ul class="whiterail-ul">.*?</ul>)"', content, re.DOTALL)
if ul_match:
    declared_len = ul_match.group(1)
    ul_content = ul_match.group(2)
    actual_len = len(ul_content.encode('utf-8'))
    print(f'UL declared length: {declared_len}')
    print(f'UL actual length: {actual_len}')
    print(f'Match: {declared_len == str(actual_len)}')
    print(f'UL preview: {ul_content[:100]}...')
else:
    print('UL pattern not found')

# Check for any remaining length mismatches
print('\nChecking for length mismatches...')
mismatches = 0
for match in re.finditer(r's:(\d+):"(.*?)"(?=;|})', content, re.DOTALL):
    declared = int(match.group(1))
    actual_content = match.group(2)
    actual = len(actual_content.encode('utf-8'))
    if declared != actual:
        mismatches += 1
        if mismatches <= 3:  # Show first 3 mismatches
            print(f'Mismatch {mismatches}: declared={declared}, actual={actual}')
            print(f'  Content preview: {repr(actual_content[:50])}')

print(f'Total mismatches found: {mismatches}')
