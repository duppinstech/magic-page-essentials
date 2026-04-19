#!/usr/bin/env python3
"""
Build Magic Page export from raw content ONLY - no template mixing
"""
import re
import csv

def sanitize_content(content):
    """Clean content for PHP serialization"""
    if not content:
        return " "
    
    # For UL content starting with *, convert to clean HTML
    if content.strip().startswith('*'):
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        li_items = []
        
        for line in lines:
            if line.startswith('*'):
                item_text = line[1:].strip()
                li_items.append(f'<li>{item_text}</li>')
        
        if li_items:
            return f'<ul class="whiterail-ul">{"".join(li_items)}</ul>'
    
    # For regular content, remove newlines and extra whitespace
    clean = re.sub(r'\n+', ' ', content)
    clean = re.sub(r'\r+', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def detect_locations(text):
    """Detect cities and states in text"""
    known_cities = ['Ringgold', 'Trenton', 'Chattanooga', 'Calhoun']
    known_states = ['GA', 'TN', 'NC', 'AL']
    
    locations = {'cities': set(), 'states': set()}
    
    for city in known_cities:
        if city in text:
            locations['cities'].add(city)
    
    for state in known_states:
        if state in text:
            locations['states'].add(state)
    
    # Convert sets to lists
    locations['cities'] = list(locations['cities'])
    locations['states'] = list(locations['states'])
    
    return locations

def replace_locations(text, locations):
    """Replace locations with shortcodes"""
    result = text
    
    # Replace cities with [location]
    for city in locations['cities']:
        result = result.replace(city, '[location]')
    
    # Handle states based on count
    if len(locations['states']) > 1:
        # Multiple states: replace all with [meta_region_code]
        for state in locations['states']:
            result = result.replace(state, '[meta_region_code]')
    elif len(locations['states']) == 1:
        # Single state: replace NC with actual state, others with [meta_region_code]
        actual_state = locations['states'][0]
        result = result.replace('NC', actual_state)  # Template has NC, replace with actual
        for state in locations['states']:
            if state != 'NC':  # Don't double-replace
                result = result.replace(state, '[meta_region_code]')
    
    return result

def parse_blocks(raw_text):
    """Extract content blocks from raw text"""
    blocks = {'roadside': {'h1': [], 'ul': [], 'paragraph-1': [], 'paragraph-2': [], 
                          'paragraph-3': [], 'paragraph-4': [], 'paragraph-5': [], 'paragraph-6': []}}
    
    # Apply location shortcodes to raw text first
    locations = detect_locations(raw_text)
    processed_text = replace_locations(raw_text, locations)
    
    print(f"Detected locations: {locations}")
    
    # Split by H1 headings
    h1_pattern = r'<h1[^>]*>(.*?)</h1>'
    h1_matches = list(re.finditer(h1_pattern, processed_text, re.IGNORECASE | re.DOTALL))
    
    if h1_matches:
        # Get first H1 content
        first_h1 = h1_matches[0].group(1).strip()
        blocks['roadside']['h1'].append(sanitize_content(first_h1))
        
        # Get content after first H1
        content_after_h1 = processed_text[h1_matches[0].end():]
        
        # Extract UL content (bullet points) - only from first section
        lines = content_after_h1.split('\n')
        ul_lines = []
        
        # Stop at first H2 to avoid duplicates
        for line in lines:
            line = line.strip()
            if line.startswith('<h2') or line.startswith('<H2'):
                break
            if line.startswith('*'):
                ul_lines.append(line)
        
        if ul_lines:
            ul_content = '\n'.join(ul_lines)
            blocks['roadside']['ul'].append(sanitize_content(ul_content))
            print(f"Extracted {len(ul_lines)} bullet points for UL")
        
        # Extract paragraphs by splitting on H2 tags
        h2_pattern = r'<h2[^>]*>.*?</h2>'
        h2_parts = re.split(h2_pattern, content_after_h1, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove UL content from parts before processing paragraphs
        clean_parts = []
        for part in h2_parts:
            # Remove lines that start with *
            lines = part.split('\n')
            non_ul_lines = [line for line in lines if not line.strip().startswith('*')]
            clean_part = '\n'.join(non_ul_lines)
            clean_parts.append(clean_part)
        
        # Process each H2 section for paragraphs
        paragraph_counter = 1
        
        for i, part in enumerate(clean_parts):
            if not part.strip():
                continue
            
            # Split by double newlines to get paragraphs
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', part) if p.strip()]
            
            # Filter out unwanted content
            valid_paragraphs = []
            for p in paragraphs:
                if not p.startswith('*') and 'Button:' not in p and 'Link:' not in p:
                    valid_paragraphs.append(p)
            
            # Add paragraphs to blocks
            for j, para in enumerate(valid_paragraphs):
                if paragraph_counter <= 6:
                    field_name = f'paragraph-{paragraph_counter}'
                    blocks['roadside'][field_name].append(sanitize_content(para))
                    paragraph_counter += 1
    
    return blocks

def build_php_serialized_from_raw(blocks):
    """Build complete PHP serialized structure from raw blocks only"""
    
    # Get content from blocks
    roadside_blocks = blocks.get('roadside', {})
    
    # H1 content
    h1_content = roadside_blocks.get('h1', [' '])[0] if roadside_blocks.get('h1') else ' '
    h1_with_tags = f'<h1>{h1_content}</h1>' if h1_content != ' ' else ' '
    
    # UL content  
    ul_content = roadside_blocks.get('ul', [' '])[0] if roadside_blocks.get('ul') else ' '
    
    # Paragraph contents
    paragraphs = {}
    for i in range(1, 7):
        field_name = f'paragraph-{i}'
        content = roadside_blocks.get(field_name, [' '])[0] if roadside_blocks.get(field_name) else ' '
        paragraphs[field_name] = content
    
    # Build the PHP serialized structure
    def php_string(content):
        """Helper to create s:LENGTH:"CONTENT" """
        length = len(content.encode('utf-8'))
        return f's:{length}:"{content}"'
    
    # Build the complete structure - simplified with just the essential fields
    serialized = 'a:1:{s:18:"spintax-shortcodes";a:12:{'
    
    # Meta title
    serialized += 's:7:"c0g3b1f";a:2:{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{s:6:"8q6ubd";'
    serialized += php_string('24/7 Emergency Roadside Assistance [location], [meta_region_code] | [xfield_company-name]')
    serialized += ';}}'
    
    # Meta description  
    serialized += 's:6:"ex59ys";a:2:{s:5:"label";s:18:"roadside-meta-desc";s:7:"options";a:1:{s:6:"ttpvck";'
    serialized += php_string('[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call [xfield_phone-tel] for fuel delivery, vehicle lockouts, battery jumps, & more.')
    serialized += ';}}'
    
    # H1
    serialized += 's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";'
    serialized += php_string(h1_with_tags)
    serialized += ';}}'
    
    # H2-1
    serialized += 's:5:"g92x2";a:2:{s:5:"label";s:13:"roadside-h2-1";s:7:"options";a:1:{s:6:"8mch6i";'
    serialized += php_string('<h2>Emergency [xfield_roadside-keyword] Services in [location], [meta_region_code]</h2>')
    serialized += ';}}'
    
    # IMG-1 (simple placeholder)
    serialized += 's:5:"nyfvy";a:2:{s:5:"label";s:14:"roadside-img-1";s:7:"options";a:1:{s:6:"icqjo8";'
    serialized += php_string('<img class="size-medium wp-image-1811 alignleft" src="[xfield_img-url]" width="300" height="225" alt="[xfield_roadside-keyword] [location]">')
    serialized += ';}}'
    
    # Paragraph 1
    serialized += 's:5:"a71va";a:2:{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{s:6:"rc9iod";'
    serialized += php_string(paragraphs['paragraph-1'])
    serialized += ';}}'
    
    # Paragraph 2
    serialized += 's:6:"wxkwza";a:2:{s:5:"label";s:20:"roadside-paragraph-2";s:7:"options";a:1:{s:5:"vl1dc";'
    serialized += php_string(paragraphs['paragraph-2'])
    serialized += ';}}'
    
    # H2-2
    serialized += 's:6:"3wnz47";a:2:{s:5:"label";s:13:"roadside-h2-2";s:7:"options";a:1:{s:5:"9zek4";'
    serialized += php_string('<h2>Get Quick [xfield_roadside-keyword] Near Me in [location], [meta_region_code]</h2>')
    serialized += ';}}'
    
    # IMG-2
    serialized += 's:5:"wirda";a:2:{s:5:"label";s:14:"roadside-img-2";s:7:"options";a:1:{s:6:"siiztr";'
    serialized += php_string('<img class="size-medium wp-image-1811 alignleft" src="[xfield_img-url]" width="300" height="225" alt="[xfield_roadside-keyword] [location]">')
    serialized += ';}}'
    
    # Paragraph 3
    serialized += 's:5:"fldy3";a:2:{s:5:"label";s:20:"roadside-paragraph-3";s:7:"options";a:1:{s:6:"cz8bsk";'
    serialized += php_string(paragraphs['paragraph-3'])
    serialized += ';}}'
    
    # Paragraph 4
    serialized += 's:5:"q5man";a:2:{s:5:"label";s:20:"roadside-paragraph-4";s:7:"options";a:1:{s:6:"r9x286";'
    serialized += php_string(paragraphs['paragraph-4'])
    serialized += ';}}'
    
    # UL field
    serialized += 's:6:"feebkl";a:2:{s:5:"label";s:11:"roadside-ul";s:7:"options";a:1:{s:6:"9vxk2p";'
    serialized += php_string(ul_content)
    serialized += ';}}'
    
    # Button
    serialized += 's:6:"btn123";a:2:{s:5:"label";s:12:"roadside-btn";s:7:"options";a:1:{s:6:"4lzqbp";'
    serialized += php_string('Call [xfield_company-name] for [xfield_roadside-keyword] in [location], [meta_region_code] Now!')
    serialized += ';}}'
    
    # Close the structure
    serialized += '}}'
    
    return serialized

def main():
    # Read raw content
    with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    print("Building Magic Page export from RAW CONTENT ONLY...")
    
    # Parse blocks from raw content
    blocks = parse_blocks(raw_text)
    
    # Build PHP serialized structure
    output = build_php_serialized_from_raw(blocks)
    
    # Write output
    with open('magicpage_from_raw_only.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✅ Generated: magicpage_from_raw_only.txt ({len(output)} bytes)")
    
    # Create review CSV
    review_data = []
    roadside_blocks = blocks.get('roadside', {})
    
    for field_type in ['h1', 'ul', 'paragraph-1', 'paragraph-2', 'paragraph-3', 'paragraph-4', 'paragraph-5', 'paragraph-6']:
        content = roadside_blocks.get(field_type, [])
        if content:
            review_data.append([field_type, content[0][:100] + ('...' if len(content[0]) > 100 else '')])
        else:
            review_data.append([field_type, '(empty - using space)'])
    
    with open('magicpage_review_raw_only.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Field', 'Content Preview'])
        writer.writerows(review_data)
    
    print("✅ Generated: magicpage_review_raw_only.csv")

if __name__ == "__main__":
    main()
