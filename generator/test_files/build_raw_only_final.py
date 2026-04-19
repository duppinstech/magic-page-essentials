#!/usr/bin/env python3
import re

print("Building final file with ONLY raw content - NO sample content ever used")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
if h1_match:
    h1_text = h1_match.group(1).strip()
    # Apply shortcodes
    h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
    h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
    h1_content = f'<h1>{h1_text}</h1>'
else:
    h1_content = " "

# Extract paragraphs (text blocks)
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*'):
                # Apply shortcodes
                p_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', line)
                p_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', p_text)
                p_text = p_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
                paragraphs.append(f'<p>{p_text}</p>')

# Extract UL items
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)
if ul_items:
    processed_items = []
    for item in ul_items:
        item = item.strip()
        # Apply shortcodes
        item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item)
        item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
        processed_items.append(f'<li>{item}</li>')
    ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'
else:
    ul_content = " "

print(f"Extracted: H1={len(h1_content)} chars, Paragraphs={len(paragraphs)} items, UL={len(ul_content)} chars")

# Start with the working sample structure but replace ALL content
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace H1 - ONLY use raw content
h1_length = len(h1_content.encode('utf-8'))
template = re.sub(r's:\d+:"<h1>[^<]*</h1>"', f's:{h1_length}:"{h1_content}"', template, count=1)
print(f"✅ Replaced H1 with raw content ({h1_length} bytes)")

# Replace ALL paragraphs - map raw paragraphs to option IDs
paragraph_mappings = [
    ('rc9iod', 0), ('armq2', 1), ('x58wh', 2), ('u3ql0n', 3),
    ('vl1dc', 0), ('zwqt7', 1), ('pqtkyq', 2), ('jitca', 3),
    ('cz8bsk', 0), ('yzjhed', 1), ('dblfsd', 2), ('n01p7o', 3),
    ('r9x286', 0), ('g6m6l', 1), ('9cyet8', 2), ('o4p9w', 3)
]

for option_id, para_index in paragraph_mappings:
    if para_index < len(paragraphs):
        para_content = paragraphs[para_index]
    else:
        para_content = " "  # Blank for missing
        
    para_length = len(para_content.encode('utf-8'))
    # Replace both length and content
    template = re.sub(f'(s:6:"{option_id}";s:)\\d+(:"[^"]*")', f'\\g<1>{para_length}\\g<2>', template)
    template = re.sub(f'(s:6:"{option_id}";s:{para_length}:")([^"]*)(")', f'\\g<1>{para_content}\\g<3>', template)

print(f"✅ Replaced {len(paragraph_mappings)} paragraph fields with raw content")

# Replace ALL UL fields with raw content
ul_length = len(ul_content.encode('utf-8'))
ul_option_ids = ['9vxk2p', 'rddpm7', 'febl7d', 'g5jbni']
for ul_id in ul_option_ids:
    # Replace length and content
    template = re.sub(f'(s:6:"{ul_id}";s:)\\d+(:"<ul[^"]*")', f'\\g<1>{ul_length}\\g<2>', template, flags=re.DOTALL)
    template = re.sub(f'(s:6:"{ul_id}";s:{ul_length}:")(<ul.*?</ul>)(")', f'\\g<1>{ul_content}\\g<3>', template, flags=re.DOTALL)

print(f"✅ Replaced all UL fields with raw content ({ul_length} bytes)")

# Write final file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created: magicpage_import_from_txt.txt (100% RAW CONTENT ONLY)")

# Test it
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization works with 100% raw content!')
except Exception as e:
    print(f'❌ PHP error: {e}')

# Verify NO sample content
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

sample_phrases = [
    "Our team of top-notch operators",
    "Coastal Towing",
    "Rocky Mount",
    "Wilson County",
    "Gazebos Towing"
]

for phrase in sample_phrases:
    if phrase in content:
        print(f"❌ FOUND SAMPLE CONTENT: {phrase}")
    else:
        print(f"✅ No '{phrase}' found")

print("✅ Sample content verification complete")
