#!/usr/bin/env python3
import re

print("ADDING PARAGRAPHS TO THE WORKING CLEAN VERSION")

# First, create the working clean version
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Apply the working H1 replacement
h1_pattern = r's:\d+:"<h1>[^<]*</h1>"'
h1_replacement = 's:64:"<h1>24/7 Roadside Assistance [location], [meta_region_code]</h1>"'
content = re.sub(h1_pattern, h1_replacement, content, count=1)

# Step 2: Apply the working UL replacement
ul_content = '<ul class="whiterail-ul"><li>Jump Start [location], [meta_region_code]</li><li>Emergency Battery Service [location], [meta_region_code]</li><li>Battery Boost Service [location], [meta_region_code]</li><li>Flat Tire Change [location], [meta_region_code]</li><li>Fuel Delivery Near Me [location], [meta_region_code]</li><li>Gas Delivery Service [location], [meta_region_code]</li><li>Out of Gas Fuel Delivery [location], [meta_region_code]</li><li>Winch-out Service [location], [meta_region_code]</li><li>Ditch Pull-Outs [location], [meta_region_code]</li><li>Locked out of Car Service [location], [meta_region_code]</li><li>Vehicle Lockout Service [location], [meta_region_code]</li><li>Light Duty Towing [location], [meta_region_code]</li><li>Medium Duty Towing [location], [meta_region_code]</li><li>Heavy Duty Towing [location], [meta_region_code]</li><li>Truck Roadside Service [location], [meta_region_code]</li><li>Towing [location], [meta_region_code]</li></ul>'

ul_length = len(ul_content.encode('utf-8'))
ul_pattern = r's:\d+:"<ul class="whiterail-ul">.*?</ul>"'
ul_replacement = f's:{ul_length}:"{ul_content}"'
content = re.sub(ul_pattern, ul_replacement, content, flags=re.DOTALL)

print("✅ Applied working H1 and UL replacements")

# Test this baseline first
import phpserialize
try:
    phpserialize.loads(content.encode('utf-8'))
    print("✅ Baseline working version still good")
except Exception as e:
    print(f"❌ Baseline broken: {e}")
    exit(1)

# Step 3: Now carefully add raw paragraph content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

# Extract first few good paragraphs from raw
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
good_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 50:  # Only longer, substantial lines
                p_text = apply_shortcodes(line)
                good_paragraphs.append(p_text)
                if len(good_paragraphs) >= 10:  # Limit to first 10 good paragraphs
                    break
        if len(good_paragraphs) >= 10:
            break

print(f"Extracted {len(good_paragraphs)} good paragraphs")

# Replace ONLY the first few paragraph fields to test
paragraph_count = 0

def careful_paragraph_replacer(match):
    global paragraph_count
    if paragraph_count < len(good_paragraphs):
        para_text = good_paragraphs[paragraph_count]
        paragraph_count += 1
        para_content = f'<p>{para_text}</p>'
        para_length = len(para_content.encode('utf-8'))
        return f's:{para_length}:"{para_content}"'
    else:
        # Keep original for now
        return match.group(0)

# Replace only first 5 paragraphs to test
original_content = content
for i in range(5):
    paragraph_count = i
    content = re.sub(r's:\d+:"<p>.*?</p>"', careful_paragraph_replacer, content, count=1, flags=re.DOTALL)
    
    # Test after each replacement
    try:
        phpserialize.loads(content.encode('utf-8'))
        print(f"✅ Successfully added paragraph {i+1}")
    except Exception as e:
        print(f"❌ Error after paragraph {i+1}: {e}")
        content = original_content  # Revert
        break

# Write the result
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Final test
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! File with paragraphs passes PHP serialization! ({len(test_data)} bytes)')
    
    # Count content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    h1_count = final_content.count('<h1>')
    p_count = final_content.count('<p>')
    ul_count = final_content.count('<ul>')
    print(f"✅ Content: {h1_count} H1, {p_count} paragraphs, {ul_count} UL sections")
    print(f"✅ [location] shortcodes: {'[location]' in final_content}")
    print(f"✅ [xfield_company-name] shortcodes: {'[xfield_company-name]' in final_content}")
    
except Exception as e:
    print(f'❌ Final PHP error: {e}')
