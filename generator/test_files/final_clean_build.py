#!/usr/bin/env python3
import re

print("FINAL BUILD: Raw content only + working PHP structure")

# Read raw content and process it
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Process H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = h1_match.group(1).strip() if h1_match else "Raw H1"
h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
h1_content = f'<h1>{h1_text}</h1>'

# Process first paragraph
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
first_paragraph = " "
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        if lines:
            line = lines[0]
            if line and not line.startswith('*'):
                p_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', line)
                p_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', p_text)
                p_text = p_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
                first_paragraph = f'<p>{p_text}</p>'
                break

# Process UL - just first few items to keep it manageable
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)[:5]  # Just 5 items
processed_items = []
for item in ul_items:
    item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item.strip())
    item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
    processed_items.append(f'<li>{item}</li>')
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Processed: H1={len(h1_content)}, Para={len(first_paragraph)}, UL={len(ul_content)}")

# Use the working sample but replace content carefully
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace H1 carefully
h1_length = len(h1_content.encode('utf-8'))
template = re.sub(r's:\d+:"<h1>[^<]*</h1>"', f's:{h1_length}:"{h1_content}"', template, count=1)

# Replace first paragraph option (rc9iod) with raw content
para_length = len(first_paragraph.encode('utf-8'))
template = re.sub(r'(s:6:"rc9iod";s:)\d+(:"[^"]*")', f'\\g<1>{para_length}\\g<2>', template)
template = re.sub(f'(s:6:"rc9iod";s:{para_length}:")([^"]*)(")', f'\\g<1>{first_paragraph}\\g<3>', template)

# Replace first UL option (9vxk2p) with raw content
ul_length = len(ul_content.encode('utf-8'))
template = re.sub(r'(s:6:"9vxk2p";s:)\d+(:"<ul[^"]*")', f'\\g<1>{ul_length}\\g<2>', template, flags=re.DOTALL)
template = re.sub(f'(s:6:"9vxk2p";s:{ul_length}:")(<ul.*?</ul>)(")', f'\\g<1>{ul_content}\\g<3>', template, flags=re.DOTALL)

# Now systematically replace ALL other content with blanks
def fix_all_string_lengths(content):
    def replacer(match):
        string_content = match.group(2)
        actual_length = len(string_content.encode('utf-8'))
        return f's:{actual_length}:"{string_content}"'
    
    return re.sub(r's:(\d+):"(.*?)"(?=;|})', replacer, content, flags=re.DOTALL)

# Replace all remaining sample content with blanks, but keep the structure
sample_patterns = [
    r's:\d+:"[^"]*Our team of top-notch operators[^"]*"',
    r's:\d+:"[^"]*Coastal Towing[^"]*"',
    r's:\d+:"[^"]*Wilson County[^"]*"', 
    r's:\d+:"[^"]*Gazebos Towing[^"]*"',
    r's:\d+:"[^"]*Rocky Mount[^"]*"'
]

for pattern in sample_patterns:
    template = re.sub(pattern, 's:1:" "', template, flags=re.DOTALL)

# Fix all string lengths
template = fix_all_string_lengths(template)

# Write final file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created final file")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization works!')
    
    # Final verification - check for sample content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    sample_phrases = ["Our team of top-notch operators", "Coastal Towing", "Wilson County", "Gazebos Towing"]
    all_clean = True
    for phrase in sample_phrases:
        if phrase in content:
            print(f"❌ FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ CLEAN: {phrase}")
    
    if all_clean:
        print("🎉 FINAL SUCCESS: NO sample content + working PHP!")
    
except Exception as e:
    print(f'❌ PHP error: {e}')
