#!/usr/bin/env python3
import re

print("CAREFULLY ADDING RAW PARAGRAPHS TO WORKING VERSION")

# Read the working version
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("Starting with verified working version")

# Read and extract raw paragraphs
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

# Extract good paragraphs from raw
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
raw_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 50:
                p_text = apply_shortcodes(line)
                raw_paragraphs.append(p_text)

print(f"Extracted {len(raw_paragraphs)} raw paragraphs")

# Replace specific paragraph option IDs with raw content
# These are the main paragraph option IDs from the template
target_paragraphs = [
    'rc9iod',  # roadside-paragraph-1 option 1
    'armq2',   # roadside-paragraph-1 option 2  
    'x58wh',   # roadside-paragraph-1 option 3
    'vl1dc',   # roadside-paragraph-2 option 1
    'zwqt7',   # roadside-paragraph-2 option 2
    'cz8bsk',  # roadside-paragraph-3 option 1
    'yzjhed',  # roadside-paragraph-3 option 2
    'r9x286',  # roadside-paragraph-4 option 1
    'g6m6l'    # roadside-paragraph-4 option 2
]

# Replace each target paragraph with raw content
for i, option_id in enumerate(target_paragraphs):
    if i < len(raw_paragraphs):
        para_text = raw_paragraphs[i]
        para_content = f'<p>{para_text}</p>'
        para_length = len(para_content.encode('utf-8'))
        
        # Find and replace this specific option ID
        pattern = f'(s:6:"{option_id}";s:)\\d+(:"[^"]*")'
        replacement = f'\\g<1>{para_length}\\g<2>'
        content = re.sub(pattern, replacement, content)
        
        # Replace the actual content
        content_pattern = f'(s:6:"{option_id}";s:{para_length}:")([^"]*)(";)'
        content_replacement = f'\\g<1>{para_content}\\g<3>'
        content = re.sub(content_pattern, content_replacement, content, flags=re.DOTALL)
        
        print(f"✅ Replaced paragraph {option_id} with raw content")
        
        # Test after each replacement
        import phpserialize
        try:
            phpserialize.loads(content.encode('utf-8'))
            print(f"   ✅ PHP serialization still works")
        except Exception as e:
            print(f"   ❌ PHP error after {option_id}: {e}")
            break

# Write the enhanced version
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Final test
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'\n🎉 SUCCESS! Enhanced file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Count content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    # Check for sample content
    sample_content = ["Our team of top-notch operators", "Coastal Towing", "Wilson County", "Gazebos Towing"]
    all_clean = True
    for phrase in sample_content:
        if phrase in final_content:
            print(f"❌ FOUND sample: {phrase}")
            all_clean = False
        else:
            print(f"✅ CLEAN: {phrase}")
    
    h1_count = final_content.count('<h1>')
    p_count = final_content.count('<p>')
    ul_count = final_content.count('<ul>')
    print(f"✅ Content: {h1_count} H1, {p_count} paragraphs, {ul_count} UL sections")
    print(f"✅ [location] shortcodes: {'[location]' in final_content}")
    print(f"✅ [xfield_company-name] shortcodes: {'[xfield_company-name]' in final_content}")
    
    if all_clean:
        print("\n🎉 COMPLETE SUCCESS: Working version with raw paragraphs and NO sample contamination!")
    
except Exception as e:
    print(f'\n❌ Final PHP error: {e}')
