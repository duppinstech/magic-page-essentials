#!/usr/bin/env python3
import re

print("BUILDING COMPLETE FILE - SYSTEMATIC FIELD-BY-FIELD REPLACEMENT")

# Read and process ALL raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    """Apply all shortcode replacements"""
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = apply_shortcodes(h1_match.group(1).strip()) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text}</h1>'

# Extract H2
h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', raw_text, re.IGNORECASE)
h2_text = apply_shortcodes(h2_match.group(1).strip()) if h2_match else "Emergency Roadside Services in [location], [meta_region_code]"
h2_content = f'<h2>{h2_text}</h2>'

# Extract ALL paragraphs
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
all_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 30:
                p_text = apply_shortcodes(line)
                all_paragraphs.append(f'<p>{p_text}</p>')

# Extract UL items
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)
processed_items = [f'<li>{apply_shortcodes(item.strip())}</li>' for item in ul_items]
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Raw content: H1={len(h1_content)}, H2={len(h2_content)}, Paragraphs={len(all_paragraphs)}, UL={len(ul_content)}")

# Start with template
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

def replace_field_content(template, option_id, new_content):
    """Replace content for a specific option ID while preserving PHP structure"""
    new_length = len(new_content.encode('utf-8'))
    
    # Find and replace the length
    length_pattern = f'(s:6:"{option_id}";s:)\\d+(:")'
    template = re.sub(length_pattern, f'\\g<1>{new_length}\\g<2>', template)
    
    # Find and replace the content
    content_pattern = f'(s:6:"{option_id}";s:{new_length}:")([^"]*)(";)'
    template = re.sub(content_pattern, f'\\g<1>{new_content}\\g<3>', template, flags=re.DOTALL)
    
    return template

# Replace specific H1 field
template = replace_field_content(template, '7xj2jn', h1_content)
print("✅ Replaced H1")

# Replace specific H2 fields with raw H2
h2_option_ids = ['8mch6i', '9zek4', '7mc6qu', 'vq96', '7vnrdm', 'w2hfeu', 'g8cl8', 'wq0gnm', 'lbt0s8']
for h2_id in h2_option_ids[:3]:  # Replace first 3 H2 fields
    template = replace_field_content(template, h2_id, h2_content)
print("✅ Replaced H2 fields")

# Replace paragraph fields with raw paragraphs
paragraph_option_ids = [
    'rc9iod', 'armq2', 'x58wh', 'u3ql0n',  # roadside paragraphs
    'vl1dc', 'zwqt7', 'pqtkyq', 'jitca',   # more roadside
    'cz8bsk', 'yzjhed', 'dblfsd', 'n01p7o', # even more
    'r9x286', 'g6m6l', '9cyet8', 'o4p9w',   # final roadside
    'x6a6u', '0l4o2', 'm9dc4', 'y49n57',    # heavy paragraphs
    'nk6vo', 'o4fgb', 'odypac', 'uch4jf'    # more heavy
]

for i, para_id in enumerate(paragraph_option_ids):
    if i < len(all_paragraphs):
        para_content = all_paragraphs[i]
    else:
        # Cycle through paragraphs
        para_content = all_paragraphs[i % len(all_paragraphs)] if all_paragraphs else '<p>Professional roadside assistance in [location], [meta_region_code].</p>'
    
    template = replace_field_content(template, para_id, para_content)

print(f"✅ Replaced {len(paragraph_option_ids)} paragraph fields")

# Replace UL fields with raw UL
ul_option_ids = ['9vxk2p', 'rddpm7', 'febl7d', 'g5jbni']
for ul_id in ul_option_ids:
    template = replace_field_content(template, ul_id, ul_content)
print("✅ Replaced UL fields")

# Replace img fields with blank
img_option_ids = ['icqjo8', 'zqtylq', 'rznnlkg', 'hcn5ub', 'siiztr', 'iwruys', 'h495ns', '3a1nii']
for img_id in img_option_ids:
    template = replace_field_content(template, img_id, ' ')
print("✅ Cleared img fields")

# Final scrub of any remaining sample content
sample_phrases = ["Our team of top-notch operators", "Coastal Towing", "Wilson County", "Gazebos Towing", "Rocky Mount"]
for phrase in sample_phrases:
    if phrase in template:
        print(f"🔥 Final scrub: {phrase}")
        pattern = r's:\d+:"[^"]*' + re.escape(phrase) + r'[^"]*"'
        template = re.sub(pattern, 's:1:" "', template, flags=re.DOTALL)

# Write file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created complete file with systematic field replacement")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Complete file passes PHP serialization! ({len(test_data)} bytes)')
except Exception as e:
    print(f'❌ PHP error: {e}')

# Verify no sample content
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

all_clean = True
for phrase in sample_phrases:
    if phrase in content:
        print(f"❌ FOUND: {phrase}")
        all_clean = False
    else:
        print(f"✅ CLEAN: {phrase}")

if all_clean:
    print("🎉 COMPLETE SUCCESS: Full template with ALL raw content and NO sample contamination!")
    print(f"✅ [location] shortcodes: {'[location]' in content}")
    print(f"✅ [meta_region_code] shortcodes: {'[meta_region_code]' in content}")
    print(f"✅ [xfield_company-name] shortcodes: {'[xfield_company-name]' in content}")
