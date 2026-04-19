#!/usr/bin/env python3
import re

with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    sample = f.read()

# Find UL content in sample
ul_match = re.search(r's:\d+:"(<ul class=.*?</ul>)"', sample, re.DOTALL)
if ul_match:
    sample_ul = ul_match.group(1)
    print('Sample UL content:')
    print(repr(sample_ul[:200]))
    print()
    print('Quote handling in sample:')
    if '\\"' in sample_ul:
        print('Sample uses escaped quotes \\"')
    else:
        print('Sample uses raw quotes')
        
    # Check exact quote usage
    print(f'Raw quotes count: {sample_ul.count('"')}')
    print(f'Escaped quotes count: {sample_ul.count('\\"')}')
else:
    print('No UL found in sample')

# Test if sample works
import phpserialize
try:
    with open('magicpage_export_sample.txt', 'rb') as f:
        sample_data = f.read()
    phpserialize.loads(sample_data)
    print('✅ Sample file works')
except Exception as e:
    print(f'❌ Sample error: {e}')
