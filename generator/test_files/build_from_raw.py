#!/usr/bin/env python3
import re

# Step 1: Read and process raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# Step 2: Extract and prepare all content pieces
def extract_content(raw_text):
    """Extract all content pieces from raw text"""
    content = {}
    
    # Extract H1 (case insensitive)
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.DOTALL | re.IGNORECASE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        # Apply location replacements
        h1_text = h1_text.replace('Bell\'s Towing & Recovery', '[xfield_company-name]')
        h1_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', h1_text)
        h1_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', h1_text)
        content['h1'] = f'<h1>{h1_text}</h1>'
    
    # Extract paragraphs (text blocks between H2 tags and other content)
    # Split by H1/H2 tags and get text blocks
    sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
    processed_paragraphs = []
    
    for section in sections:
        section = section.strip()
        if section and not section.startswith('*'):  # Skip bullet points
            # Split into sentences/paragraphs by line breaks
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            for line in lines:
                if line and not line.startswith('*'):
                    # Apply location replacements
                    p_text = line.replace('Bell\'s Towing & Recovery', '[xfield_company-name]')
                    p_text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', p_text)
                    p_text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', p_text)
                    processed_paragraphs.append(f'<p>{p_text}</p>')
    
    content['paragraphs'] = processed_paragraphs
    
    # Extract UL content
    ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)
    if ul_items:
        processed_items = []
        for item in ul_items:
            item = item.strip()
            # Apply location replacements
            item = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', item)
            item = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', item)
            processed_items.append(f'<li>{item}</li>')
        
        content['ul'] = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'
    
    return content

# Step 3: Get processed content
processed_content = extract_content(raw_text)

print("Extracted content:")
print(f"H1: {len(processed_content.get('h1', ''))} chars")
print(f"Paragraphs: {len(processed_content.get('paragraphs', []))} items")
print(f"UL: {len(processed_content.get('ul', ''))} chars")

# Step 4: Build the PHP serialized structure
def build_serialized_file(content):
    """Build the complete serialized file from processed content"""
    
    # Read template for structure
    with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace H1
    if 'h1' in content:
        h1_content = content['h1']
        h1_length = len(h1_content.encode('utf-8'))
        h1_pattern = r's:\d+:"<h1>[^<]*</h1>"'
        h1_replacement = f's:{h1_length}:"{h1_content}"'
        template = re.sub(h1_pattern, h1_replacement, template, count=1)
        print(f"✅ Replaced H1 ({h1_length} bytes)")
    
    # Replace paragraphs - map to specific option IDs
    paragraph_mappings = [
        ('rc9iod', 0), ('armq2', 1), ('x58wh', 2), ('u3ql0n', 3),
        ('vl1dc', 0), ('zwqt7', 1), ('pqtkyq', 2), ('jitca', 3),
        ('cz8bsk', 0), ('yzjhed', 1), ('dblfsd', 2), ('n01p7o', 3),
        ('r9x286', 0), ('g6m6l', 1), ('9cyet8', 2), ('o4p9w', 3)
    ]
    
    paragraphs = content.get('paragraphs', [])
    
    for option_id, para_index in paragraph_mappings:
        if para_index < len(paragraphs):
            para_content = paragraphs[para_index]
        else:
            para_content = " "  # Blank space for missing paragraphs
            
        para_length = len(para_content.encode('utf-8'))
        para_pattern = f'(s:6:"{option_id}";s:)\\d+(:"[^"]*")'
        para_replacement = f'\\g<1>{para_length}\\g<2>'
        template = re.sub(para_pattern, para_replacement, template)
        
        # Replace content
        content_pattern = f'(s:6:"{option_id}";s:{para_length}:")([^"]*)(")'
        content_replacement = f'\\g<1>{para_content}\\g<3>'
        template = re.sub(content_pattern, content_replacement, template)
    
    print(f"✅ Replaced {len(paragraph_mappings)} paragraph fields")
    
    # Replace UL content
    if 'ul' in content:
        ul_content = content['ul']
        ul_length = len(ul_content.encode('utf-8'))
        
        # Replace all UL fields
        ul_option_ids = ['9vxk2p', 'rddpm7', 'febl7d', 'g5jbni']
        for ul_id in ul_option_ids:
            # Replace length
            ul_pattern = f'(s:6:"{ul_id}";s:)\\d+(:"<ul[^"]*")'
            ul_replacement = f'\\g<1>{ul_length}\\g<2>'
            template = re.sub(ul_pattern, ul_replacement, template, flags=re.DOTALL)
            
            # Replace content
            content_pattern = f'(s:6:"{ul_id}";s:{ul_length}:")(<ul.*?</ul>)(")'
            content_replacement = f'\\g<1>{ul_content}\\g<3>'
            template = re.sub(content_pattern, content_replacement, template, flags=re.DOTALL)
        
        print(f"✅ Replaced UL content in all fields ({ul_length} bytes)")
    
    return template

# Step 5: Build final file
final_content = build_serialized_file(processed_content)

# Step 6: Write and test
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Created: magicpage_import_from_txt.txt")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization works!')
except Exception as e:
    print(f'❌ PHP error: {e}')
