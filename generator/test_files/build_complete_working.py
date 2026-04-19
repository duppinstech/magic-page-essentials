#!/usr/bin/env python3
import re

print("BUILDING COMPLETE FILE USING EXACT WORKING APPROACH")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

# Extract raw paragraphs (clean text blocks)
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
raw_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 30:
                p_text = apply_shortcodes(line)
                raw_paragraphs.append(p_text)  # Just the text, not wrapped in <p> yet

print(f"Extracted {len(raw_paragraphs)} raw paragraph texts")

# Start with the working sample (EXACT same approach as clean_fix.py)
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("Starting with working sample...")

# Step 1: Replace H1 content (EXACT same as working version)
h1_pattern = r's:\d+:"<h1>[^<]*</h1>"'
h1_replacement = 's:64:"<h1>24/7 Roadside Assistance [location], [meta_region_code]</h1>"'
content = re.sub(h1_pattern, h1_replacement, content, count=1)
print("✅ Replaced H1 content")

# Step 2: Replace ALL paragraph content with raw paragraphs
paragraph_index = 0

def paragraph_replacer(match):
    global paragraph_index
    if paragraph_index < len(raw_paragraphs):
        para_text = raw_paragraphs[paragraph_index]
        paragraph_index += 1
    else:
        # Cycle back through paragraphs
        para_text = raw_paragraphs[paragraph_index % len(raw_paragraphs)] if raw_paragraphs else "Professional roadside assistance in [location], [meta_region_code]."
        paragraph_index += 1
    
    # Wrap in <p> tags
    para_content = f'<p>{para_text}</p>'
    para_length = len(para_content.encode('utf-8'))
    return f's:{para_length}:"{para_content}"'

# Replace ALL paragraph patterns
content = re.sub(r's:\d+:"<p>.*?</p>"', paragraph_replacer, content, flags=re.DOTALL)
print(f"✅ Replaced paragraphs with {paragraph_index} raw paragraph texts")

# Step 3: Replace UL content (EXACT same as working version)
ul_content = '<ul class="whiterail-ul"><li>Jump Start [location], [meta_region_code]</li><li>Emergency Battery Service [location], [meta_region_code]</li><li>Battery Boost Service [location], [meta_region_code]</li><li>Flat Tire Change [location], [meta_region_code]</li><li>Fuel Delivery Near Me [location], [meta_region_code]</li><li>Gas Delivery Service [location], [meta_region_code]</li><li>Out of Gas Fuel Delivery [location], [meta_region_code]</li><li>Winch-out Service [location], [meta_region_code]</li><li>Ditch Pull-Outs [location], [meta_region_code]</li><li>Locked out of Car Service [location], [meta_region_code]</li><li>Vehicle Lockout Service [location], [meta_region_code]</li><li>Light Duty Towing [location], [meta_region_code]</li><li>Medium Duty Towing [location], [meta_region_code]</li><li>Heavy Duty Towing [location], [meta_region_code]</li><li>Truck Roadside Service [location], [meta_region_code]</li><li>Towing [location], [meta_region_code]</li></ul>'

ul_length = len(ul_content.encode('utf-8'))

# Replace ALL UL content carefully (EXACT same pattern as working version)
ul_pattern = r's:\d+:"<ul class="whiterail-ul">.*?</ul>"'
ul_replacement = f's:{ul_length}:"{ul_content}"'
content = re.sub(ul_pattern, ul_replacement, content, flags=re.DOTALL)
print(f"✅ Replaced UL content ({ul_length} bytes)")

# Step 4: Clear img content
content = re.sub(r's:\d+:"<img.*?>"', 's:1:" "', content, flags=re.DOTALL)
print("✅ Cleared img content")

# Step 5: Final scrub of sample content
sample_content = ["Our team of top-notch operators", "Coastal Towing", "Wilson County", "Gazebos Towing", "Rocky Mount"]
for sample in sample_content:
    if sample in content:
        print(f"🔥 Scrubbing: {sample}")
        pattern = r's:\d+:"[^"]*' + re.escape(sample) + r'[^"]*"'
        content = re.sub(pattern, 's:1:" "', content, flags=re.DOTALL)

# Write the complete file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Created COMPLETE file using exact working approach")

# Test it (EXACT same test as working version)
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Complete file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Verify no sample content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    all_clean = True
    for phrase in sample_content:
        if phrase in final_content:
            print(f"❌ FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ CLEAN: {phrase}")
    
    if all_clean:
        print("🎉 COMPLETE SUCCESS!")
        print(f"✅ [location] shortcodes: {'[location]' in final_content}")
        print(f"✅ [meta_region_code] shortcodes: {'[meta_region_code]' in final_content}")
        print(f"✅ [xfield_company-name] shortcodes: {'[xfield_company-name]' in final_content}")
        
        # Count content
        h1_count = final_content.count('<h1>')
        p_count = final_content.count('<p>')
        ul_count = final_content.count('<ul>')
        print(f"✅ Content: {h1_count} H1, {p_count} paragraphs, {ul_count} UL sections")
        
except Exception as e:
    print(f'❌ PHP error: {e}')

# Quick structure check (same as working version)
clean_open = content.count('{')
clean_close = content.count('}')
clean_semi = content.count(';')
print(f"Structure check: {{ {clean_open}, }} {clean_close}, ; {clean_semi}")
