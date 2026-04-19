#!/usr/bin/env python3
import re

def escape_quotes_in_serialized_strings(content):
    """Escape quotes within PHP serialized strings"""
    def replacer(match):
        declared_length = match.group(1)
        string_content = match.group(2)
        
        # Escape any quotes within the string content
        escaped_content = string_content.replace('"', '\\"')
        
        # Recalculate length after escaping
        actual_length = len(escaped_content.encode('utf-8'))
        
        return f's:{actual_length}:"{escaped_content}"'
    
    # Match PHP serialized strings and escape quotes within them
    return re.sub(r's:(\d+):"(.*?)"(?=;|})', replacer, content, flags=re.DOTALL)

# Read current file
with open('magicpage_import_from_txt_FINAL.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original file size: {len(content)} chars')

# Escape quotes in serialized strings
fixed_content = escape_quotes_in_serialized_strings(content)

print(f'Fixed file size: {len(fixed_content)} chars')

# Write fixed version
with open('magicpage_import_from_txt_QUOTES_FIXED.txt', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('Created: magicpage_import_from_txt_QUOTES_FIXED.txt')

# Test the fixed version
import phpserialize
try:
    with open('magicpage_import_from_txt_QUOTES_FIXED.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('✅ SUCCESS! File passes PHP serialization!')
except Exception as e:
    print(f'❌ Still error: {e}')
