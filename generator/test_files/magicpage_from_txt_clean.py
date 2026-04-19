#!/usr/bin/env python3
"""
Magic Page content processor - Template-based approach
Uses the working sample as a template and replaces content placeholders
"""

import re
import sys

def normalize_tags(text):
    """Convert HTML tags to lowercase"""
    text = re.sub(r'<(/?)([hH])([0-9])>', r'<\1h\3>', text)
    return text

def strip_tags(text):
    """Remove HTML tags from text"""
    return re.sub(r'<[^>]+>', '', text)

def classify_keyword(text):
    """Classify content based on H1 text"""
    text = text.lower()
    if 'equipment' in text:
        return 'equipment'
    elif 'heavy' in text:
        return 'heavy'
    elif 'roadside' in text:
        return 'roadside'
    elif 'towing' in text:
        return 'towing'
    else:
        return 'roadside'

def detect_locations(text):
    """Detect city and state names in text"""
    # Known cities and states from the sample
    known_cities = ['Ringgold', 'Chattanooga', 'Calhoun', 'Trenton']
    known_states = ['GA', 'TN']
    
    locations = {'cities': [], 'states': []}
    
    for city in known_cities:
        if city in text:
            locations['cities'].append(city)
    
    for state in known_states:
        if f', {state}' in text or f' {state}' in text:
            locations['states'].append(state)
    
    return locations

def replace_locations(text, locations):
    """Replace city and state names with shortcodes"""
    # Replace cities with [location]
    for city in locations['cities']:
        text = re.sub(r'\b' + re.escape(city) + r'\b', '[location]', text, flags=re.IGNORECASE)
    
    # Replace states with [meta_region_code]
    for state in locations['states']:
        text = re.sub(r'\b' + re.escape(state) + r'\b', '[meta_region_code]', text, flags=re.IGNORECASE)
    
    return text

def parse_blocks(raw_text):
    """Parse content blocks from raw text"""
    text = normalize_tags(raw_text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Split by H1 tags
    parts = re.split(r"(?=<h1>)", text)
    parts = [p for p in parts if p.strip()]
    blocks = {}
    
    for part in parts:
        m = re.search(r"<h1>(.*?)</h1>", part, re.S)
        if not m:
            continue
        h1_text = strip_tags(m.group(1))
        kw = classify_keyword(h1_text)
        
        # Skip if we already processed this keyword (use first occurrence only)
        if kw in blocks:
            continue
            
        if kw not in blocks:
            blocks[kw] = {}
        
        # Extract H1 content
        blocks[kw]["h1"] = [h1_text]
        
        # For roadside content, extract specific paragraphs based on structure
        if kw == 'roadside':
            # Extract paragraphs from the raw content between H2 sections
            # Remove H1 and H2 tags but keep the text content
            content_text = re.sub(r'<h1>.*?</h1>', '', part, flags=re.IGNORECASE)
            
            # Split by H2 tags to get sections
            sections = re.split(r'<h2[^>]*>.*?</h2>', content_text, flags=re.IGNORECASE)
            
            # Extract all paragraphs from all sections
            all_paragraphs = []
            for section in sections:
                section = section.strip()
                if section:
                    # Split by line breaks and filter for substantial content
                    section_paras = [p.strip() for p in section.split('\n') if p.strip() and len(p.strip()) > 50]
                    all_paragraphs.extend(section_paras)
            
            # Assign the first 4 substantial paragraphs to specific fields
            if len(all_paragraphs) >= 1:
                blocks[kw]["paragraph-1"] = [all_paragraphs[0]]
            if len(all_paragraphs) >= 2:
                blocks[kw]["paragraph-3"] = [all_paragraphs[1]]  # This should be the Bell's Towing paragraph
            if len(all_paragraphs) >= 3:
                blocks[kw]["paragraph-4"] = [all_paragraphs[2]]
            if len(all_paragraphs) >= 4:
                blocks[kw]["paragraph-5"] = [all_paragraphs[3]]
            
            # Set paragraph-2 and paragraph-6 to empty space as per your instructions
            blocks[kw]["paragraph-2"] = [" "]
            blocks[kw]["paragraph-6"] = [" "]
        else:
            # For other keywords, use simpler extraction
            text_content = strip_tags(part)
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip() and len(p.strip()) > 50]
            
            for i, para in enumerate(paragraphs[:6], 1):
                if para != h1_text.strip():  # Skip the H1 text itself
                    blocks[kw][f"paragraph-{i}"] = [para]
    
    return blocks

def create_template_based_export(blocks):
    """Use working sample as template and replace content placeholders"""
    
    # Read the working sample as our template
    with open("magicpage_export_sample.txt", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Debug: Print what content was extracted
    print("=== EXTRACTED CONTENT FOR REPLACEMENT ===")
    if 'roadside' in blocks:
        roadside_blocks = blocks['roadside']
        print(f"H1: {roadside_blocks.get('h1', ['NOT FOUND'])[0]}")
        for i in range(1, 7):
            para_key = f'paragraph-{i}'
            if para_key in roadside_blocks:
                content = roadside_blocks[para_key][0]
                print(f"Para-{i}: {content[:80]}...")
            else:
                print(f"Para-{i}: NOT FOUND")
    
    # Extract actual content from blocks for the roadside keyword
    if 'roadside' in blocks:
        roadside_blocks = blocks['roadside']
        
        # Replace H1 content (keeping the exact structure and IDs)
        if 'h1' in roadside_blocks and roadside_blocks['h1']:
            h1_content = roadside_blocks['h1'][0]
            print(f"=== H1 REPLACEMENT ===")
            print(f"Original H1: {h1_content}")
            
            # Apply location replacement to H1
            locs = detect_locations(h1_content)
            h1_replaced = replace_locations(h1_content, locs)
            print(f"After location replacement: {h1_replaced}")
            
            # Find and replace the H1 content in template while keeping structure
            # Pattern: s:6:"7xj2jn";s:XX:"CONTENT_HERE"
            h1_pattern = r'(s:6:"7xj2jn";s:)\d+(:"[^"]*")'
            new_h1_content = f'<h1>{h1_replaced}</h1>'
            h1_replacement = f'\\g<1>{len(new_h1_content.encode("utf-8"))}:"{new_h1_content}"'
            print(f"New H1 content: {new_h1_content}")
            template = re.sub(h1_pattern, h1_replacement, template)
        
        # Replace paragraph content
        for i in range(1, 7):  # paragraph-1 through paragraph-6
            para_key = f'paragraph-{i}'
            if para_key in roadside_blocks and roadside_blocks[para_key]:
                para_content = roadside_blocks[para_key][0]
                
                # Apply location replacement
                locs = detect_locations(para_content)
                para_replaced = replace_locations(para_content, locs)
                print(f"Para-{i} after location replacement: {para_replaced[:80]}...")
                
                # Find the corresponding paragraph in template and replace content
                # This is complex because paragraphs have multiple options with different IDs
                # For now, replace the first option of each paragraph
                if i == 1:
                    # paragraph-1 has options: rc9iod, armq2, x58wh, u3ql0n
                    para_pattern = r'(s:6:"rc9iod";s:)\d+(:"[^"]*")'
                    para_replacement = f'\\g<1>{len(para_replaced.encode("utf-8"))}:"{para_replaced}"'
                    template = re.sub(para_pattern, para_replacement, template)
    
    return template

def save_csv(blocks, path):
    """Save blocks to CSV for review"""
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Field","Content"])
        
        for keyword, fields in blocks.items():
            for field_name, content_list in fields.items():
                full_field_name = f"{keyword}-{field_name}"
                content = content_list[0] if content_list else ""
                w.writerow([full_field_name, content])

def main():
    if len(sys.argv) < 2:
        print("Usage: python magicpage_from_txt_clean.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    out_php = "magicpage_import_from_txt.txt"
    out_csv = "magicpage_review_from_txt.csv"
    
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    blocks = parse_blocks(raw_text)
    
    # Generate the template-based export
    php_output = create_template_based_export(blocks)
    
    # Save PHP output
    with open(out_php, "w", encoding="utf-8") as f:
        f.write(php_output)
    print(f"Wrote: {out_php}")
    
    # Save CSV output
    save_csv(blocks, out_csv)
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()
