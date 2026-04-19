#!/usr/bin/env python3
"""
Magic Page content processor - Using the CORRECT simplified template structure
NO options arrays - just labels as MPP expects
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

def parse_blocks(raw_text):
    """Parse content blocks from raw text - simplified for testing"""
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
        
        # Initialize keyword block if not exists
        if kw not in blocks:
            blocks[kw] = {"h1": [], "variations": []}
        
        # Store H1 content (there will be multiple variations)
        blocks[kw]["h1"].append(h1_text)
        
        # Store this variation for processing
        blocks[kw]["variations"].append(part)
    
    # After collecting all variations, process the first variation of each keyword for content
    for kw, kw_data in blocks.items():
        if "variations" in kw_data and kw_data["variations"]:
            # Use the first variation for content extraction
            first_variation = kw_data["variations"][0]
            
            # Use the first H1 for the template
            kw_data["h1"] = [kw_data["h1"][0]] if kw_data["h1"] else [""]
            
            # Parse content following the standard structure: H1 → H2-1 → P1, P2 → H2-2 → P3, P4 → H2-3 → P5, P6 → UL → BTN
            # Remove H1 tag but keep content for processing
            content_after_h1 = re.sub(r'<h1>.*?</h1>', '', first_variation, flags=re.IGNORECASE)
            
            # Split by H2 tags to get the three main sections
            h2_sections = re.split(r'<h2[^>]*>.*?</h2>', content_after_h1, flags=re.IGNORECASE)
            
            # Process each H2 section for paragraphs
            section_paragraphs = []
            for section in h2_sections:
                section = section.strip()
                if section:
                    # Split by double line breaks to identify separate paragraphs
                    paras = [p.strip() for p in re.split(r'\n\s*\n', section) if p.strip() and len(p.strip()) > 50]
                    section_paragraphs.append(paras)
            
            # Assign paragraphs based on structure: H2-1 (P1, P2), H2-2 (P3, P4), H2-3 (P5, P6)
            if len(section_paragraphs) >= 1:  # First H2 section
                section_1_paras = section_paragraphs[0]
                if len(section_1_paras) >= 1:
                    kw_data["paragraph-1"] = [section_1_paras[0]]
                if len(section_1_paras) >= 2:
                    kw_data["paragraph-2"] = [section_1_paras[1]]
                else:
                    kw_data["paragraph-2"] = [" "]  # Empty if no P2
            
            if len(section_paragraphs) >= 2:  # Second H2 section  
                section_2_paras = section_paragraphs[1]
                if len(section_2_paras) >= 1:
                    kw_data["paragraph-3"] = [section_2_paras[0]]
                if len(section_2_paras) >= 2:
                    kw_data["paragraph-4"] = [section_2_paras[1]]
                else:
                    kw_data["paragraph-4"] = [" "]  # Empty if no P4
            
            if len(section_paragraphs) >= 3:  # Third H2 section
                section_3_paras = section_paragraphs[2]
                if len(section_3_paras) >= 1:
                    kw_data["paragraph-5"] = [section_3_paras[0]]
                if len(section_3_paras) >= 2:
                    kw_data["paragraph-6"] = [section_3_paras[1]]
                else:
                    kw_data["paragraph-6"] = [" "]  # Empty if no P6
    
    return blocks

def create_simple_template_export(blocks):
    """Add raw content to the working template structure"""
    
    # Read the correct simplified template
    with open("magicpage_template_clean.txt", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Now add content while maintaining the working structure
    # Structure: a:1:{s:5:"label";...} for empty fields
    #           a:2:{s:5:"label";...;s:7:"options";a:X:{...}} for fields with content
    
    if 'roadside' in blocks:
        roadside_blocks = blocks['roadside']
        
        # Add H1 content - convert from a:1 to a:2 structure with options
        if 'h1' in roadside_blocks and roadside_blocks['h1']:
            h1_content = roadside_blocks['h1'][0]
            h1_with_tags = f'<h1>{h1_content}</h1>'
            
            # Replace: s:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}
            # With:    s:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:LENGTH:"CONTENT";}}
            h1_old = 's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}'
            h1_new = f's:6:"pgn00b";a:2:{{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{{s:6:"7xj2jn";s:{len(h1_with_tags.encode("utf-8"))}:"{h1_with_tags}";}}}}'
            template = template.replace(h1_old, h1_new)
        
        # Add Paragraph-1 content
        if 'paragraph-1' in roadside_blocks and roadside_blocks['paragraph-1']:
            para1_content = roadside_blocks['paragraph-1'][0]
            
            # Replace: s:5:"a71va";a:1:{s:5:"label";s:20:"roadside-paragraph-1";}
            # With:    s:5:"a71va";a:2:{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{s:6:"rc9iod";s:LENGTH:"CONTENT";}}
            para1_old = 's:5:"a71va";a:1:{s:5:"label";s:20:"roadside-paragraph-1";}'
            para1_new = f's:5:"a71va";a:2:{{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{{s:6:"rc9iod";s:{len(para1_content.encode("utf-8"))}:"{para1_content}";}}}}'
            template = template.replace(para1_old, para1_new)
    
    return template

def save_csv(blocks, path):
    """Save blocks to CSV for review"""
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Field","Content"])
        
        for keyword, fields in blocks.items():
            for field_name, content_list in fields.items():
                if field_name not in ["variations"]:  # Skip internal data
                    full_field_name = f"{keyword}-{field_name}"
                    content = content_list[0] if content_list else ""
                    w.writerow([full_field_name, content])

def main():
    if len(sys.argv) < 2:
        print("Usage: python magicpage_simple_template.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    out_php = "magicpage_import_simple.txt"
    out_csv = "magicpage_review_simple.csv"
    
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    blocks = parse_blocks(raw_text)
    
    # Generate the simple template-based export
    php_output = create_simple_template_export(blocks)
    
    # Save PHP output
    with open(out_php, "w", encoding="utf-8") as f:
        f.write(php_output)
    print(f"Wrote: {out_php}")
    
    # Save CSV output
    save_csv(blocks, out_csv)
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()
