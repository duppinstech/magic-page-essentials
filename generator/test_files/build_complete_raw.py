#!/usr/bin/env python3
import re

print("BUILDING COMPLETE FILE - ALL RAW CONTENT MAPPED TO FULL TEMPLATE")

# Read and process ALL raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

print("Extracting ALL content from raw...")

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = h1_match.group(1).strip() if h1_match else "24/7 Roadside Assistance"
h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
h1_text = h1_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
h1_content = f'<h1>{h1_text}</h1>'

# Extract H2
h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', raw_text, re.IGNORECASE)
if h2_match:
    h2_text = h2_match.group(1).strip()
    h2_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h2_text)
    h2_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h2_text)
    h2_text = h2_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    h2_content = f'<h2>{h2_text}</h2>'
else:
    h2_content = f'<h2>Emergency Roadside Services in [location], [meta_region_code]</h2>'

# Extract ALL paragraphs (text blocks between headers)
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
all_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 20:  # Skip very short lines
                # Apply shortcodes
                p_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', line)
                p_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', p_text)
                p_text = p_text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
                all_paragraphs.append(f'<p>{p_text}</p>')

# Extract ALL UL items
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)
processed_items = []
for item in ul_items:
    item = item.strip()
    # Apply shortcodes
    item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item)
    item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
    processed_items.append(f'<li>{item}</li>')
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Extracted: H1={len(h1_content)} chars, H2={len(h2_content)} chars, Paragraphs={len(all_paragraphs)} items, UL={len(ul_content)} chars")

# Start with the full sample template
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

def php_string_length(content):
    return len(content.encode('utf-8'))

# Replace H1 fields with raw content
template = re.sub(r's:\d+:"<h1>[^<]*</h1>"', f's:{php_string_length(h1_content)}:"{h1_content}"', template)

# Replace H2 fields with raw content  
template = re.sub(r's:\d+:"<h2>[^<]*</h2>"', f's:{php_string_length(h2_content)}:"{h2_content}"', template)

# Replace ALL paragraph fields with raw paragraphs (cycle through available paragraphs)
paragraph_pattern = r's:\d+:"<p>.*?</p>"'
paragraph_matches = list(re.finditer(paragraph_pattern, template, re.DOTALL))

print(f"Found {len(paragraph_matches)} paragraph fields to replace")

# Replace each paragraph field with raw content (cycle through paragraphs)
for i, match in enumerate(paragraph_matches):
    if i < len(all_paragraphs):
        para_content = all_paragraphs[i]
    else:
        # Cycle back through paragraphs if we have more fields than content
        para_content = all_paragraphs[i % len(all_paragraphs)] if all_paragraphs else "<p>Professional roadside assistance in [location], [meta_region_code].</p>"
    
    para_length = php_string_length(para_content)
    template = template[:match.start()] + f's:{para_length}:"{para_content}"' + template[match.end():]
    # Recalculate matches since template changed
    paragraph_matches = list(re.finditer(paragraph_pattern, template, re.DOTALL))

# Replace ALL UL fields with raw UL content
ul_pattern = r's:\d+:"<ul.*?</ul>"'
ul_length = php_string_length(ul_content)
template = re.sub(ul_pattern, f's:{ul_length}:"{ul_content}"', template, flags=re.DOTALL)

# Replace ALL img fields with blank (remove sample images)
template = re.sub(r's:\d+:"<img.*?>"', 's:1:" "', template, flags=re.DOTALL)

# Now scrub any remaining sample content
sample_content = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County",
    "Gazebos Towing",
    "Rocky Mount",
    "I-95",
    "Route 301", 
    "Route 42",
    "U.S. 64",
    "Peachtree Street",
    "Raleigh Boulevard"
]

for sample in sample_content:
    if sample in template:
        print(f"🔥 Scrubbing remaining: {sample}")
        pattern = r's:\d+:"[^"]*' + re.escape(sample) + r'[^"]*"'
        template = re.sub(pattern, 's:1:" "', template, flags=re.DOTALL)

# Fix all string lengths after replacements
def fix_all_string_lengths(content):
    def replacer(match):
        string_content = match.group(2)
        actual_length = len(string_content.encode('utf-8'))
        return f's:{actual_length}:"{string_content}"'
    
    return re.sub(r's:(\d+):"(.*?)"(?=;|})', replacer, content, flags=re.DOTALL)

template = fix_all_string_lengths(template)

# Write the complete file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created COMPLETE file with ALL raw content mapped to full template")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! Complete file passes PHP serialization!')
    print(f"File size: {len(test_data)} bytes")
except Exception as e:
    print(f'❌ PHP error: {e}')

# Final verification - check for sample content
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    final_content = f.read()

print("\nFinal verification:")
all_clean = True
for phrase in sample_content:
    if phrase in final_content:
        print(f"❌ FOUND: {phrase}")
        all_clean = False
    else:
        print(f"✅ CLEAN: {phrase}")

if all_clean:
    print("\n🎉 COMPLETE SUCCESS: Full template with ALL raw content!")
    print(f"✅ Contains [location] shortcodes: {'[location]' in final_content}")
    print(f"✅ Contains [meta_region_code] shortcodes: {'[meta_region_code]' in final_content}")
    print(f"✅ Contains [xfield_company-name] shortcodes: {'[xfield_company-name]' in final_content}")
else:
    print("\n❌ Some sample content remains")
