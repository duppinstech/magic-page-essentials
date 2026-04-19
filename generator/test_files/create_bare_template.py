#!/usr/bin/env python3
import re

# Read the sample file to get structure only
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

print("Creating bare template - removing ALL sample content...")

# Replace ALL paragraph content with single space
template = re.sub(r's:\d+:"<p>.*?</p>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all paragraph content")

# Replace ALL H1 content with single space  
template = re.sub(r's:\d+:"<h1>.*?</h1>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all H1 content")

# Replace ALL H2 content with single space
template = re.sub(r's:\d+:"<h2>.*?</h2>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all H2 content")

# Replace ALL UL content with single space
template = re.sub(r's:\d+:"<ul.*?</ul>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all UL content")

# Replace ALL img content with single space
template = re.sub(r's:\d+:"<img.*?>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all img content")

# Replace any remaining long content strings with single space
template = re.sub(r's:\d+:"[^"]{50,}"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared all remaining long content")

# Write the bare template
with open('magicpage_bare_template.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("Created: magicpage_bare_template.txt (BARE STRUCTURE ONLY)")

# Test it
import phpserialize
try:
    with open('magicpage_bare_template.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('✅ Bare template PHP serialization works!')
except Exception as e:
    print(f'❌ Bare template error: {e}')
