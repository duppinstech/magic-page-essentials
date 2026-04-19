#!/usr/bin/env python3
import re

print("BUILDING MINIMAL FILE - ONLY RAW CONTENT")

# Read and process raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = h1_match.group(1).strip() if h1_match else "24/7 Roadside Assistance"
h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
h1_content = f'<h1>{h1_text}</h1>'

# Extract first paragraph
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
paragraph_content = " "
for section in sections:
    section = section.strip()
    if section and not section.startswith('*') and len(section) > 50:
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        if lines:
            line = lines[0]
            if line and not line.startswith('*'):
                p_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', line)
                p_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', p_text)
                p_text = p_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
                paragraph_content = f'<p>{p_text}</p>'
                break

# Extract UL items - first 8 items only
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)[:8]
processed_items = []
for item in ul_items:
    item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item.strip())
    item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
    processed_items.append(f'<li>{item}</li>')
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Raw content: H1={len(h1_content)} chars, Para={len(paragraph_content)} chars, UL={len(ul_content)} chars")

# Build minimal PHP structure manually
def php_string(content):
    length = len(content.encode('utf-8'))
    return f's:{length}:"{content}"'

# Create minimal structure with only essential fields
output = 'a:1:{s:18:"spintax-shortcodes";a:3:{'

# Field 1: H1
output += 's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";'
output += php_string(h1_content)
output += ';}}'

# Field 2: Paragraph  
output += 's:5:"a71va";a:2:{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{s:6:"rc9iod";'
output += php_string(paragraph_content)
output += ';}}'

# Field 3: UL
output += 's:6:"feebkl";a:2:{s:5:"label";s:11:"roadside-ul";s:7:"options";a:1:{s:6:"9vxk2p";'
output += php_string(ul_content)
output += ';}}'

# Close structure
output += '}}'

print(f"Built structure: {len(output)} chars")

# Write file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print("✅ Created minimal file with ONLY raw content")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    result = phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization works!')
    
    # Verify content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for any sample content
    sample_phrases = ["Our team", "Coastal", "Wilson", "Gazebos", "Rocky Mount"]
    all_clean = True
    for phrase in sample_phrases:
        if phrase in content:
            print(f"❌ Found: {phrase}")
            all_clean = False
    
    if all_clean:
        print("✅ NO sample content found!")
        print("✅ Contains [location] shortcodes:", "[location]" in content)
        print("✅ Contains [meta_region_code] shortcodes:", "[meta_region_code]" in content)
        print("✅ Contains raw UL content:", "<ul class=" in content)
        print("🎉 FINAL SUCCESS: Pure raw content with working PHP!")
    
except Exception as e:
    print(f'❌ PHP error: {e}')
