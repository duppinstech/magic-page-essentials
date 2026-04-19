#!/usr/bin/env python3
import re

def fix_all_string_lengths(content):
    def replacer(match):
        declared_length = match.group(1) 
        string_content = match.group(2)
        actual_length = len(string_content.encode('utf-8'))
        return f's:{actual_length}:"{string_content}"'
    
    return re.sub(r's:(\d+):"(.*?)"(?=;|})', replacer, content, flags=re.DOTALL)

# Read current file
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original file size: {len(content)} chars')

# Fix all string lengths
fixed_content = fix_all_string_lengths(content)

print(f'Fixed file size: {len(fixed_content)} chars')

# Write fixed version
with open('magicpage_import_from_txt_FINAL.txt', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('Created: magicpage_import_from_txt_FINAL.txt')

# Test the fixed version
import phpserialize
try:
    with open('magicpage_import_from_txt_FINAL.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('✅ FINAL file passes PHP serialization!')
except Exception as e:
    print(f'❌ FINAL file error: {e}')
