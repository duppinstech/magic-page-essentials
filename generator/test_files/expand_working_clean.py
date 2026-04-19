#!/usr/bin/env python3
import re

print("EXPANDING THE WORKING CLEAN APPROACH WITH ALL RAW CONTENT")

# Read and process raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = apply_shortcodes(h1_match.group(1).strip()) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text}</h1>'

# Extract ALL paragraphs from raw
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

print(f"Extracted: H1, {len(all_paragraphs)} paragraphs, UL with {len(ul_items)} items")

# Start with the working sample template
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# Use the WORKING approach from clean_fix.py but expand it

# 1. Replace H1 (this worked before)
h1_length = len(h1_content.encode('utf-8'))
template = re.sub(r's:\d+:"<h1>[^<]*</h1>"', f's:{h1_length}:"{h1_content}"', template, count=1)
print("✅ Replaced H1")

# 2. Replace ALL paragraph content with raw paragraphs (expand the working approach)
# Find all paragraph patterns and replace systematically
def replace_paragraph_content(content, paragraphs):
    """Replace paragraph content while preserving structure"""
    para_index = 0
    
    def replacer(match):
        nonlocal para_index
        if para_index < len(paragraphs):
            new_content = paragraphs[para_index]
            para_index += 1
        else:
            # Cycle back through paragraphs
            new_content = paragraphs[para_index % len(paragraphs)] if paragraphs else '<p>Professional service in [location], [meta_region_code].</p>'
            para_index += 1
            
        new_length = len(new_content.encode('utf-8'))
        return f's:{new_length}:"{new_content}"'
    
    return re.sub(r's:\d+:"<p>.*?</p>"', replacer, content, flags=re.DOTALL)

template = replace_paragraph_content(template, all_paragraphs)
print(f"✅ Replaced paragraphs with {len(all_paragraphs)} raw paragraphs")

# 3. Replace UL content (this worked before)
ul_length = len(ul_content.encode('utf-8'))
template = re.sub(r's:\d+:"<ul.*?</ul>"', f's:{ul_length}:"{ul_content}"', template, flags=re.DOTALL)
print("✅ Replaced UL content")

# 4. Clear img content (replace with blanks)
template = re.sub(r's:\d+:"<img.*?>"', 's:1:" "', template, flags=re.DOTALL)
print("✅ Cleared img content")

# 5. Final scrub of any remaining sample content
sample_content = ["Our team of top-notch operators", "Coastal Towing", "Wilson County", "Gazebos Towing", "Rocky Mount"]
for sample in sample_content:
    if sample in template:
        print(f"🔥 Scrubbing: {sample}")
        pattern = r's:\d+:"[^"]*' + re.escape(sample) + r'[^"]*"'
        template = re.sub(pattern, 's:1:" "', template, flags=re.DOTALL)

# 6. Fix all string lengths (the working approach)
def fix_all_string_lengths(content):
    def replacer(match):
        string_content = match.group(2)
        actual_length = len(string_content.encode('utf-8'))
        return f's:{actual_length}:"{string_content}"'
    
    return re.sub(r's:(\d+):"(.*?)"(?=;|})', replacer, content, flags=re.DOTALL)

template = fix_all_string_lengths(template)
print("✅ Fixed all string lengths")

# Write the complete file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(template)

print("✅ Created COMPLETE file with ALL raw content using working approach")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Complete file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Verify content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_clean = True
    for phrase in sample_content:
        if phrase in content:
            print(f"❌ FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ CLEAN: {phrase}")
    
    if all_clean:
        print("🎉 COMPLETE SUCCESS: Full template with ALL raw content!")
        print(f"✅ Contains [location]: {'[location]' in content}")
        print(f"✅ Contains [meta_region_code]: {'[meta_region_code]' in content}")
        print(f"✅ Contains [xfield_company-name]: {'[xfield_company-name]' in content}")
        
        # Count content fields
        h1_count = content.count('<h1>')
        p_count = content.count('<p>')
        ul_count = content.count('<ul>')
        print(f"✅ Content: {h1_count} H1, {p_count} paragraphs, {ul_count} UL sections")
    
except Exception as e:
    print(f'❌ PHP error: {e}')
