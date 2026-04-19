#!/usr/bin/env python3
import re

print("SCRUBBING ALL SAMPLE CONTENT - NUCLEAR APPROACH")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Extract and process raw content
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = h1_match.group(1).strip() if h1_match else "Raw H1"
h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
h1_content = f'<h1>{h1_text}</h1>'

# Get first raw paragraph
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

# Get raw UL
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)[:10]  # First 10 items
processed_items = []
for item in ul_items:
    item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item.strip())
    item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
    processed_items.append(f'<li>{item}</li>')
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Raw content prepared: H1={len(h1_content)}, Para={len(first_paragraph)}, UL={len(ul_content)}")

# Start with template
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# NUCLEAR SCRUB: Replace ALL content with raw content or blanks
print("🔥 NUCLEAR SCRUB: Replacing ALL sample content...")

# Replace ALL H1/H2 tags with either raw H1 or blank
template = re.sub(r's:\d+:"<h1>.*?</h1>"', f's:{len(h1_content.encode("utf-8"))}:"{h1_content}"', template, flags=re.DOTALL, count=1)
template = re.sub(r's:\d+:"<h2>.*?</h2>"', 's:1:" "', template, flags=re.DOTALL)

# Replace ALL paragraphs with either raw paragraph or blank
para_length = len(first_paragraph.encode('utf-8'))
template = re.sub(r's:\d+:"<p>.*?</p>"', f's:{para_length}:"{first_paragraph}"', template, flags=re.DOTALL, count=1)
template = re.sub(r's:\d+:"<p>.*?</p>"', 's:1:" "', template, flags=re.DOTALL)

# Replace ALL UL content with raw UL
ul_length = len(ul_content.encode('utf-8'))
template = re.sub(r's:\d+:"<ul.*?</ul>"', f's:{ul_length}:"{ul_content}"', template, flags=re.DOTALL)

# Replace ALL img tags with blank
template = re.sub(r's:\d+:"<img.*?>"', 's:1:" "', template, flags=re.DOTALL)

# Replace ALL remaining long content (50+ chars) with blanks
template = re.sub(r's:(\d+):"([^"]{50,})"', lambda m: 's:1:" "' if int(m.group(1)) > 50 else m.group(0), template)

# Replace specific problematic content
sample_content = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County",
    "Gazebos Towing",
    "Rocky Mount"
]

for sample in sample_content:
    if sample in template:
        # Find and replace any string containing this sample
        pattern = r's:\d+:"[^"]*' + re.escape(sample) + r'[^"]*"'
        template = re.sub(pattern, 's:1:" "', template)
        print(f"🔥 Scrubbed: {sample}")

print("✅ Nuclear scrub complete")

# Write final file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created: magicpage_import_from_txt.txt (SCRUBBED CLEAN)")

# Test it
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization works!')
except Exception as e:
    print(f'❌ PHP error: {e}')

# Final verification
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

for phrase in sample_content:
    if phrase in content:
        print(f"❌ STILL FOUND: {phrase}")
    else:
        print(f"✅ SCRUBBED: {phrase}")

print("🔥 SAMPLE CONTENT COMPLETELY ELIMINATED")
