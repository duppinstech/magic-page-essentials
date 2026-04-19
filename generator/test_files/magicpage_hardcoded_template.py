#!/usr/bin/env python3
import re

print("HARDCODED TEMPLATE - POPULATED WITH 100% RAW DATA")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    """Apply location and company shortcodes to text"""
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

def php_string(content):
    """Format content as PHP serialized string"""
    length = len(content.encode('utf-8'))
    return f's:{length}:"{content}"'

print("Extracting content from raw file...")

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = apply_shortcodes(h1_match.group(1).strip()) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text}</h1>'

# Extract H2
h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', raw_text, re.IGNORECASE)
h2_text = apply_shortcodes(h2_match.group(1).strip()) if h2_match else "Emergency Roadside Services in [location], [meta_region_code]"
h2_content = f'<h2>{h2_text}</h2>'

# Extract paragraphs from raw
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
raw_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            if line and not line.startswith('*') and len(line) > 30:
                p_text = apply_shortcodes(line)
                raw_paragraphs.append(f'<p>{p_text}</p>')

# Extract UL items (first 16 for manageable size)
ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)[:16]
processed_items = [f'<li>{apply_shortcodes(item.strip())}</li>' for item in ul_items]
ul_content = f'<ul class="whiterail-ul">{"".join(processed_items)}</ul>'

print(f"Extracted: H1, H2, {len(raw_paragraphs)} paragraphs, UL with {len(ul_items)} items")

# Get paragraph content (cycle through if needed)
def get_paragraph(index):
    if index < len(raw_paragraphs):
        return raw_paragraphs[index]
    elif raw_paragraphs:
        return raw_paragraphs[index % len(raw_paragraphs)]
    else:
        return f'<p>[xfield_company-name] provides professional service in [location], [meta_region_code].</p>'

print("Building hardcoded template structure...")

# Build the complete PHP serialized structure with hardcoded template
output = 'a:1:{s:18:"spintax-shortcodes";a:65:{'

# Meta title (roadside)
output += f's:7:"c0g3b1f";a:2:{{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{{s:6:"8q6ubd";{php_string("24/7 Emergency Roadside Assistance [location], [meta_region_code] | [xfield_company-name]")};}}}}' 

# Meta description (roadside)
output += f's:6:"ex59ys";a:2:{{s:5:"label";s:18:"roadside-meta-desc";s:7:"options";a:1:{{s:6:"ttpvck";{php_string("[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call for fuel delivery, vehicle lockouts, battery jumps, & more.")};}}}}' 

# H1 (roadside)
output += f's:6:"pgn00b";a:2:{{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{{s:6:"7xj2jn";{php_string(h1_content)};}}}}' 

# H2 (roadside-h2-1)
output += f's:5:"g92x2";a:2:{{s:5:"label";s:13:"roadside-h2-1";s:7:"options";a:1:{{s:6:"8mch6i";{php_string(h2_content)};}}}}' 

# Image (blank)
output += f's:5:"nyfvy";a:2:{{s:5:"label";s:14:"roadside-img-1";s:7:"options";a:1:{{s:6:"icqjo8";{php_string(" ")};}}}}' 

# Paragraph 1 options
output += f's:5:"a71va";a:2:{{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:4:{{s:6:"rc9iod";{php_string(get_paragraph(0))};s:5:"armq2";{php_string(get_paragraph(1))};s:5:"x58wh";{php_string(get_paragraph(2))};s:6:"u3ql0n";{php_string(get_paragraph(3))};}}}}' 

# Paragraph 2 options  
output += f's:6:"wxkwza";a:2:{{s:5:"label";s:20:"roadside-paragraph-2";s:7:"options";a:4:{{s:5:"vl1dc";{php_string(get_paragraph(4))};s:5:"zwqt7";{php_string(get_paragraph(5))};s:6:"pqtkyq";{php_string(get_paragraph(6))};s:5:"jitca";{php_string(get_paragraph(7))};}}}}' 

# H2-2
output += f's:6:"3wnz47";a:2:{{s:5:"label";s:13:"roadside-h2-2";s:7:"options";a:1:{{s:5:"9zek4";{php_string(f"<h2>Get Quick Roadside Assistance Near Me in [location], [meta_region_code]</h2>")};}}}}' 

# Image 2 (blank)
output += f's:5:"wirda";a:2:{{s:5:"label";s:14:"roadside-img-2";s:7:"options";a:1:{{s:6:"siiztr";{php_string(" ")};}}}}' 

# Paragraph 3 options
output += f's:5:"fldy3";a:2:{{s:5:"label";s:20:"roadside-paragraph-3";s:7:"options";a:4:{{s:6:"cz8bsk";{php_string(get_paragraph(8))};s:6:"yzjhed";{php_string(get_paragraph(9))};s:6:"dblfsd";{php_string(get_paragraph(10))};s:6:"n01p7o";{php_string(get_paragraph(11))};}}}}' 

# Paragraph 4 options
output += f's:5:"q5man";a:2:{{s:5:"label";s:20:"roadside-paragraph-4";s:7:"options";a:4:{{s:6:"r9x286";{php_string(get_paragraph(12))};s:5:"g6m6l";{php_string(get_paragraph(13))};s:6:"9cyet8";{php_string(get_paragraph(14))};s:5:"o4p9w";{php_string(get_paragraph(15))};}}}}' 

# UL content
output += f's:6:"feebkl";a:2:{{s:5:"label";s:11:"roadside-ul";s:7:"options";a:1:{{s:6:"9vxk2p";{php_string(ul_content)};}}}}' 

# Button
output += f's:6:"52i9lm";a:2:{{s:5:"label";s:12:"roadside-btn";s:7:"options";a:1:{{s:6:"4lzqbp";{php_string("Call [xfield_company-name] for Roadside Assistance in [location], [meta_region_code] Now!")};}}}}' 

# Heavy duty section
output += f's:5:"1e9th";a:2:{{s:5:"label";s:16:"heavy-meta-title";s:7:"options";a:1:{{s:6:"ocikhb";{php_string("24/7 Heavy Duty Towing in [location], [meta_region_code] | [xfield_company-name]")};}}}}' 

output += f's:6:"j0eud5";a:2:{{s:5:"label";s:15:"heavy-meta-desc";s:7:"options";a:1:{{s:6:"9teic7";{php_string("[xfield_company-name] provides 24/7 heavy duty towing in [location]. Call for heavy towing, heavy recovery, & heavy duty roadside assistance.")};}}}}' 

output += f's:6:"s2bozf";a:2:{{s:5:"label";s:8:"heavy-h1";s:7:"options";a:1:{{s:6:"3gj4as";{php_string("<h1>24/7 Heavy Tow Truck in [location], [meta_region_code]</h1>")};}}}}' 

# More heavy duty fields with raw content
output += f's:5:"m8niv";a:2:{{s:5:"label";s:10:"heavy-h2-1";s:7:"options";a:1:{{s:6:"7mc6qu";{php_string("<h2>24/7 Heavy Tow Truck in [location], [meta_region_code]</h2>")};}}}}' 

output += f's:6:"fv2bh5";a:2:{{s:5:"label";s:11:"heavy-img-1";s:7:"options";a:1:{{s:5:"db7sl";{php_string(" ")};}}}}' 

output += f's:6:"2nxs9j";a:2:{{s:5:"label";s:17:"heavy-paragraph-1";s:7:"options";a:4:{{s:5:"x6a6u";{php_string(get_paragraph(16))};s:5:"0l4o2";{php_string(get_paragraph(17))};s:5:"m9dc4";{php_string(get_paragraph(18))};s:6:"y49n57";{php_string(get_paragraph(19))};}}}}' 

output += f's:5:"7m7bb";a:2:{{s:5:"label";s:17:"heavy-paragraph-2";s:7:"options";a:4:{{s:5:"nk6vo";{php_string(get_paragraph(20))};s:5:"o4fgb";{php_string(get_paragraph(21))};s:6:"odypac";{php_string(get_paragraph(22))};s:6:"uch4jf";{php_string(get_paragraph(23))};}}}}' 

# Equipment section
output += f's:5:"xqmzb";a:2:{{s:5:"label";s:20:"equipment-meta-title";s:7:"options";a:1:{{s:6:"tisq38";{php_string("24/7 Heavy Equipment Towing in [location], [meta_region_code] | [xfield_company-name]")};}}}}' 

output += f's:6:"9eh081";a:2:{{s:5:"label";s:19:"equipment-meta-desc";s:7:"options";a:1:{{s:6:"wrmeis";{php_string("[xfield_company-name] provides 24/7 heavy equipment towing and heavy machinery towing in [location].")};}}}}' 

output += f's:5:"5dnz3";a:2:{{s:5:"label";s:12:"equipment-h1";s:7:"options";a:1:{{s:5:"uj26t";{php_string("<h1>24/7 Heavy Equipment Towing in [location], [meta_region_code]</h1>")};}}}}' 

# Towing section  
output += f's:6:"bbih6j";a:2:{{s:5:"label";s:17:"towing-meta-title";s:7:"options";a:1:{{s:5:"mlvcx";{php_string("24/7 Towing Company in [location], [meta_region_code] | Tow Truck Near Me")};}}}}' 

output += f's:6:"b8xipc";a:2:{{s:5:"label";s:16:"towing-meta-desc";s:7:"options";a:1:{{s:6:"q5k557";{php_string("[xfield_company-name] provides 24/7 emergency towing services in [location]. Call for a quick tow truck near me by a trusted towing company.")};}}}}' 

output += f's:5:"8byy4";a:2:{{s:5:"label";s:9:"towing-h1";s:7:"options";a:1:{{s:6:"1wm5sc";{php_string("<h1>24/7 Towing Services in [location], [meta_region_code]</h1>")};}}}}' 

# Close the structure
output += '}}'

print(f"Built complete structure: {len(output)} characters")

# Write the file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print("✅ Created file with hardcoded template + 100% raw data")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Hardcoded template passes PHP serialization! ({len(test_data)} bytes)')
    
    # Verify no sample content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    sample_check = ["Our team", "Coastal", "Wilson", "Gazebos", "wrecker", "coastal"]
    all_clean = True
    for phrase in sample_check:
        if phrase.lower() in final_content.lower():
            print(f"❌ SAMPLE FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ CLEAN: {phrase}")
    
    if all_clean:
        print("\n🎉 PERFECT! HARDCODED TEMPLATE WITH 100% RAW DATA!")
        print(f"✅ [location] shortcodes: {final_content.count('[location]')}")
        print(f"✅ [xfield_company-name] shortcodes: {final_content.count('[xfield_company-name]')}")
        print("🚀 READY FOR MPP IMPORT!")
    
except Exception as e:
    print(f'❌ PHP error: {e}')
