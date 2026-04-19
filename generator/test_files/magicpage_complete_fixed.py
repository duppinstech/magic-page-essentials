#!/usr/bin/env python3
import re
import phpserialize

print("COMPLETE TEMPLATE WITH ALL UL ITEMS AND PROPER IMAGES - 100% RAW DATA")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text, detected_location=None, detected_state=None, use_state_shortcode=True):
    # Use detected location and state if provided, otherwise use hardcoded fallbacks
    if detected_location:
        text = re.sub(r'\b' + re.escape(detected_location) + r'\b', '[location]', text)
    else:
        # Fallback to hardcoded locations
        text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton|Lincoln|Oxford|Pell City|Anniston)\b', '[location]', text)
    
    # Only use state shortcode if there are multiple states in the content
    if use_state_shortcode:
        if detected_state:
            text = re.sub(r'\b' + re.escape(detected_state) + r'\b', '[meta_region_code]', text)
        else:
            # Fallback to hardcoded states
            text = re.sub(r'\b(GA|TN|AL)\b', '[meta_region_code]', text)
    # If use_state_shortcode is False, leave the actual state name in the content
    
    # Replace company names (detect dynamically)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    text = text.replace("Twin Creeks Towing", "[xfield_company-name]")
    return text

print("Processing raw content...")

# Extract H1 and detect location/state dynamically
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
detected_location = None
detected_state = None

if h1_match:
    h1_text = h1_match.group(1).strip()
    print(f"Found H1: {h1_text}")
    
    # Extract location and state from H1 format: "24/7 Roadside Assistance Lincoln, AL"
    # Pattern: find the last comma and extract what's before and after it
    parts = h1_text.split(',')
    if len(parts) >= 2:
        # Get the last part (should be the state)
        state_part = parts[-1].strip()
        # Get everything before the last comma, then extract the last word(s)
        before_comma = parts[-2].strip()
        # Split by spaces and get the last word(s) that look like a city name
        words = before_comma.split()
        # Find the last word that's not a number or common words
        location_words = []
        for word in reversed(words):
            if word.isdigit() or word.lower() in ['assistance', 'roadside', 'towing', 'service', 'services']:
                break
            location_words.insert(0, word)
        
        if location_words and len(state_part) == 2 and state_part.isupper():
            detected_location = ' '.join(location_words)
            detected_state = state_part
        else:
            detected_location = None
            detected_state = None
    else:
        detected_location = None
        detected_state = None
    if detected_location and detected_state:
        print(f"Detected location: '{detected_location}', state: '{detected_state}'")
    else:
        print("Could not detect location/state from H1")
else:
    print("No H1 found in raw content")

# Check if there are multiple states in the raw content
print("Analyzing states in raw content...")
# Look for state abbreviations that are likely to be actual states
# Pattern: word, space, 2-letter state abbreviation (like "Lincoln, AL")
state_pattern = r'\b\w+(?:\s+\w+)*,\s+([A-Z]{2})\b'
found_states = set(re.findall(state_pattern, raw_text))
print(f"Found states in raw content: {sorted(found_states)}")

# Also check for standalone state abbreviations that are common US states
common_states = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'}

# Filter found states to only include actual US state abbreviations
actual_states = found_states.intersection(common_states)
print(f"Actual US states found: {sorted(actual_states)}")

# Determine if we should use state shortcode
use_state_shortcode = len(actual_states) > 1
if use_state_shortcode:
    print("Multiple states detected - will use [meta_region_code] shortcode")
else:
    print("Single state detected - will keep actual state name in content")

# Apply shortcodes with detected location/state
h1_text_processed = apply_shortcodes(h1_text, detected_location, detected_state, use_state_shortcode) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text_processed}</h1>'

# Extract content by complete versions (H1 to next H1)
print("Extracting content by complete versions...")
version_pattern = r'<H1[^>]*>.*?</H1>(.*?)(?=<H1[^>]*>|$)'
version_matches = re.findall(version_pattern, raw_text, re.DOTALL | re.IGNORECASE)

print(f"Found {len(version_matches)} complete versions")

# Process each version to extract structured content
version_data = []
for i, version_content in enumerate(version_matches):
    print(f"Processing version {i+1}...")
    
    # Extract H1 from this version
    h1_match = re.search(r'<H1[^>]*>(.*?)</H1>', version_content, re.IGNORECASE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        h1_processed = apply_shortcodes(h1_text, detected_location, detected_state, use_state_shortcode)
        h1_content = f'<h1>{h1_processed}</h1>'
    else:
        h1_content = f'<h1>24/7 Roadside Assistance [location], {detected_state}</h1>'
    
    # Extract H2s and paragraphs from this version
    h2s = re.findall(r'<H2[^>]*>(.*?)</H2>', version_content, re.IGNORECASE)
    paragraphs = []
    
    # Split by H2 tags to get paragraphs between them
    h2_sections = re.split(r'<H2[^>]*>.*?</H2>', version_content, flags=re.IGNORECASE)
    for section in h2_sections:
        lines = section.strip().split('\n')
        for line in lines:
            line = line.strip()
            if (line and not line.startswith('*') and len(line) > 30 and 
                not line.lower().startswith('button:') and 
                not line.lower().startswith('link:') and
                not line.startswith('_') and
                not line.lower().startswith('tel:') and
                not line.startswith('________________')):
                p_text = apply_shortcodes(line, detected_location, detected_state, use_state_shortcode)
                paragraphs.append(f'<p>{p_text}</p>')
    
    version_data.append({
        'h1': h1_content,
        'h2s': h2s,
        'paragraphs': paragraphs
    })
    print(f"  Version {i+1}: {len(h2s)} H2s, {len(paragraphs)} paragraphs")

# Flatten paragraphs for backward compatibility
raw_paragraphs = []
for version in version_data:
    raw_paragraphs.extend(version['paragraphs'])

# Extract ALL UL items (complete list)
all_ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)

# Process UL items with shortcodes applied
processed_ul_items = []
for item in all_ul_items:
    processed_item = apply_shortcodes(item.strip(), detected_location, detected_state, use_state_shortcode)
    processed_ul_items.append(processed_item)

print(f"Raw content: H1, {len(raw_paragraphs)} paragraphs, {len(processed_ul_items)} UL items")

def get_paragraph(index):
    if index < len(raw_paragraphs):
        return raw_paragraphs[index]
    elif raw_paragraphs:
        return raw_paragraphs[index % len(raw_paragraphs)]
    else:
        return f'<p>[xfield_company-name] provides professional service in [location], {detected_state}.</p>'

def get_paragraph_by_version(version_index, paragraph_index):
    """Get a specific paragraph from a specific version"""
    if version_index < len(version_data):
        version_paragraphs = version_data[version_index]['paragraphs']
        if paragraph_index < len(version_paragraphs):
            return version_paragraphs[paragraph_index]
        elif version_paragraphs:
            return version_paragraphs[paragraph_index % len(version_paragraphs)]
    
    # Fallback
    return f'<p>[xfield_company-name] provides professional service in [location], {detected_state}.</p>'

def get_h2_by_version(version_index, h2_index):
    """Get a specific H2 from a specific version"""
    if version_index < len(version_data):
        version_h2s = version_data[version_index]['h2s']
        if h2_index < len(version_h2s):
            h2_text = version_h2s[h2_index]
            h2_processed = apply_shortcodes(h2_text, detected_location, detected_state, use_state_shortcode)
            return f'<h2>{h2_processed}</h2>'
    
    # Fallback
    return f'<h2>Professional Service in [location], {detected_state}</h2>'

def get_paragraphs_by_section(section, paragraph_index):
    """Get paragraphs for a specific section and paragraph index across all 4 versions"""
    # Map sections to version ranges
    section_ranges = {
        'roadside': (0, 3),    # Versions 0-3
        'heavy': (4, 7),       # Versions 4-7  
        'equipment': (8, 11),  # Versions 8-11
        'towing': (12, 15)     # Versions 12-15
    }
    
    if section in section_ranges:
        start_version, end_version = section_ranges[section]
        return {
            "version1": get_paragraph_by_version(start_version, paragraph_index),
            "version2": get_paragraph_by_version(start_version + 1, paragraph_index),
            "version3": get_paragraph_by_version(start_version + 2, paragraph_index),
            "version4": get_paragraph_by_version(start_version + 3, paragraph_index)
        }
    else:
        # Fallback
        fallback = f'<p>[xfield_company-name] provides professional service in [location], {detected_state}.</p>'
        return {
            "version1": fallback,
            "version2": fallback,
            "version3": fallback,
            "version4": fallback
        }

def create_wp_image(src_filename, alt_text, section):
    """Create WordPress formatted image with proper class and dimensions"""
    # Map sections to xfield keywords
    section_keywords = {
        'roadside': 'roadside',
        'heavy': 'heavy',
        'equipment': 'equipment', 
        'towing': 'towing'
    }
    
    keyword = section_keywords.get(section, 'service')
    
    return f'<img class="size-medium wp-image-1811 alignleft" src="{src_filename}" alt="{alt_text}" width="300" height="225" />'

# Helper to create proper UL blocks with multiple LI items
def create_ul_block(items, items_per_option=20):
    """Create UL options where each option contains a UL with multiple LI items"""
    ul_dict = {}
    key_options = ["9vxk2p", "rddpm7", "6f5bza", "q1gbzg", "7xj2jn", "rc9iod", "armq2", "x58wh", "u3ql0n", "2k8fgh", 
                   "cz8bsk", "yzjhed", "dblfsd", "n01p7o", "r9x286", "g6m6l", "9cyet8", "o4p9w", "0ltva", "cnsb2c",
                   "w00bpu", "actg0a", "dbs1hl", "wpjh5s2", "x6a6u", "0l4o2", "m9dc4", "y49n57", "nk6vo", "o4fgb"]
    
    # Create multiple UL options, each with multiple LI items
    option_count = min(10, (len(items) + items_per_option - 1) // items_per_option)  # Max 10 options
    
    for i in range(option_count):
        start_idx = i * items_per_option
        end_idx = min(start_idx + items_per_option, len(items))
        
        # Create LI items for this option
        li_items = []
        for j in range(start_idx, end_idx):
            if j < len(items):
                li_items.append(f'<li>{items[j]}</li>')
        
        # Create the complete UL block
        if li_items:
            key = key_options[i % len(key_options)]
            ul_content = f"<ul class='whiterail-ul'>{''.join(li_items)}</ul>"
            ul_dict[key] = ul_content
    
    return ul_dict

# Build complete structure using Python dict, then serialize with phpserialize
print("Building complete structure with ALL UL items and proper images...")

# Create the structure as a Python dictionary
structure = {
    b'spintax-shortcodes': {}
}

fields = structure[b'spintax-shortcodes']

# Helper function to add a field
def add_field(field_id, label, options_dict):
    fields[field_id.encode('utf-8')] = {
        b'label': label.encode('utf-8'),
        b'options': {k.encode('utf-8'): v.encode('utf-8') for k, v in options_dict.items()}
    }

# Helper function to replace state shortcodes in content
def replace_state_shortcodes(content):
    if use_state_shortcode:
        return content  # Keep shortcodes if multiple states
    else:
        return content.replace('[meta_region_code]', detected_state)  # Replace with actual state

# ROADSIDE SECTION
meta_title_state = "[meta_region_code]" if use_state_shortcode else detected_state
add_field("c0g3b1f", "roadside-meta-title", {
    "8q6ubd": f"24/7 Emergency Roadside Assistance [location], {meta_title_state} | [xfield_company-name]"
})

add_field("ex59ys", "roadside-meta-desc", {
    "ttpvck": "[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call for fuel delivery, vehicle lockouts, battery jumps, & more."
})

add_field("pgn00b", "roadside-h1", {
    "7xj2jn": h1_content
})

add_field("g92x2", "roadside-h2-1", {
    "8mch6i": f"<h2>Emergency Roadside Services in [location], {meta_title_state}</h2>"
})

add_field("nyfvy", "roadside-img-1", {
    "icqjo8": replace_state_shortcodes(create_wp_image("[xfield_company-name]-roadside-assistance-[location]-[meta_region_code].jpg", "24/7 [xfield_roadside-keyword] [location] AL", "roadside")),
    "zqtylq": replace_state_shortcodes(create_wp_image("[xfield_company-name]-emergency-roadside-[location]-[meta_region_code].jpg", "Emergency [xfield_roadside-keyword] Services [location] AL", "roadside")),
    "rznnlkg": replace_state_shortcodes(create_wp_image("[xfield_company-name]-towing-service-[location]-[meta_region_code].jpg", "Professional [xfield_roadside-keyword] Service [location] AL", "roadside")),
    "hcn5ub": replace_state_shortcodes(create_wp_image("[xfield_company-name]-roadside-help-[location]-[meta_region_code].jpg", "[xfield_roadside-keyword] Help [location] AL", "roadside"))
})

# Get roadside paragraphs using helper function
roadside_p1 = get_paragraphs_by_section('roadside', 0)
add_field("a71va", "roadside-paragraph-1", {
    "rc9iod": roadside_p1["version1"],
    "armq2": roadside_p1["version2"],
    "x58wh": roadside_p1["version3"],
    "u3ql0n": roadside_p1["version4"]
})

roadside_p2 = get_paragraphs_by_section('roadside', 1)
add_field("wxkwza", "roadside-paragraph-2", {
    "vl1dc": roadside_p2["version1"],
    "zwqt7": roadside_p2["version2"],
    "pqtkyq": roadside_p2["version3"],
    "jitca": roadside_p2["version4"]
})

add_field("3wnz47", "roadside-h2-2", {
    "9zek4": "<h2>Get Quick Roadside Assistance Near Me in [location], [meta_region_code]</h2>"
})

add_field("wirda", "roadside-img-2", {
    "siiztr": replace_state_shortcodes(create_wp_image("[xfield_company-name]-quick-roadside-[location]-[meta_region_code].jpg", "Quick [xfield_roadside-keyword] Assistance [location] AL", "roadside")),
    "iwruys": replace_state_shortcodes(create_wp_image("[xfield_company-name]-fast-towing-[location]-[meta_region_code].jpg", "Fast [xfield_roadside-keyword] Service [location] AL", "roadside")),
    "h495ns": replace_state_shortcodes(create_wp_image("[xfield_company-name]-emergency-tow-[location]-[meta_region_code].jpg", "Emergency [xfield_roadside-keyword] Truck [location] AL", "roadside")),
    "3a1nii": replace_state_shortcodes(create_wp_image("[xfield_company-name]-roadside-rescue-[location]-[meta_region_code].jpg", "[xfield_roadside-keyword] Rescue [location] AL", "roadside"))
})

roadside_p3 = get_paragraphs_by_section('roadside', 2)
add_field("fldy3", "roadside-paragraph-3", {
    "cz8bsk": roadside_p3["version1"],
    "yzjhed": roadside_p3["version2"],
    "dblfsd": roadside_p3["version3"],
    "n01p7o": roadside_p3["version4"]
})

roadside_p4 = get_paragraphs_by_section('roadside', 3)
add_field("q5man", "roadside-paragraph-4", {
    "r9x286": roadside_p4["version1"],
    "g6m6l": roadside_p4["version2"],
    "9cyet8": roadside_p4["version3"],
    "o4p9w": roadside_p4["version4"]
})

# ROADSIDE UL with proper structure (first 80 UL items)
roadside_items = processed_ul_items[:80] if len(processed_ul_items) >= 80 else processed_ul_items
add_field("feebkl", "roadside-ul", create_ul_block(roadside_items))

add_field("52i9lm", "roadside-btn", {
    "4lzqbp": f"Call [xfield_company-name] for Roadside Assistance in [location], {meta_title_state} Now!",
    "wb7x8v": f"Get Roadside Assistance in [location], {meta_title_state} Now!"
})

# Since roadside versions only have 5 paragraphs (0-4), use paragraph 4 for both 5 and 6
roadside_p5 = get_paragraphs_by_section('roadside', 4)
add_field("ypk9mb", "roadside-paragraph-5", {
    "0ltva": roadside_p5["version1"],
    "cnsb2c": roadside_p5["version2"],
    "w00bpu": roadside_p5["version3"],
    "actg0a": roadside_p5["version4"]
})

# For paragraph 6, use paragraph 4 again (since there's no paragraph 5)
roadside_p6 = get_paragraphs_by_section('roadside', 4)
add_field("j3sasf", "roadside-paragraph-6", {
    "dbs1hl": roadside_p6["version1"],
    "1tffej": roadside_p6["version2"],
    "70vbk8": roadside_p6["version3"],
    "wpjh5s2": roadside_p6["version4"]
})

# HEAVY SECTION
add_field("1e9th", "heavy-meta-title", {
    "ocikhb": f"24/7 Heavy Duty Towing in [location], {meta_title_state} | [xfield_company-name]"
})

add_field("j0eud5", "heavy-meta-desc", {
    "9teic7": "[xfield_company-name] provides 24/7 heavy duty towing in [location]. Call for heavy towing, heavy recovery, & heavy duty roadside assistance."
})

add_field("s2bozf", "heavy-h1", {
    "3gj4as": "<h1>24/7 Heavy Tow Truck in [location], [meta_region_code]</h1>"
})

add_field("m8niv", "heavy-h2-1", {
    "7mc6qu": "<h2>24/7 Heavy Tow Truck in [location], [meta_region_code]</h2>"
})

add_field("fv2bh5", "heavy-img-1", {
    "db7sl": replace_state_shortcodes(create_wp_image("[xfield_company-name]-heavy-duty-towing-[location]-[meta_region_code].jpg", "[xfield_heavy-keyword] Duty Towing [location] AL", "heavy")),
    "561yep": replace_state_shortcodes(create_wp_image("[xfield_company-name]-big-rig-towing-[location]-[meta_region_code].jpg", "Big Rig [xfield_heavy-keyword] [location] AL", "heavy")),
    "9oe81q": replace_state_shortcodes(create_wp_image("[xfield_company-name]-semi-truck-towing-[location]-[meta_region_code].jpg", "Semi Truck [xfield_heavy-keyword] [location] AL", "heavy")),
    "xjsi7d": replace_state_shortcodes(create_wp_image("[xfield_company-name]-commercial-towing-[location]-[meta_region_code].jpg", "Commercial [xfield_heavy-keyword] [location] AL", "heavy"))
})

# Get heavy paragraphs using helper function
heavy_p1 = get_paragraphs_by_section('heavy', 0)
add_field("2nxs9j", "heavy-paragraph-1", {
    "x6a6u": heavy_p1["version1"],
    "0l4o2": heavy_p1["version2"],
    "m9dc4": heavy_p1["version3"],
    "y49n57": heavy_p1["version4"]
})

heavy_p2 = get_paragraphs_by_section('heavy', 1)
add_field("7m7bb", "heavy-paragraph-2", {
    "nk6vo": heavy_p2["version1"],
    "o4fgb": heavy_p2["version2"],
    "odypac": heavy_p2["version3"],
    "uch4jf": heavy_p2["version4"]
})

add_field("m6bsc", "heavy-h2-2", {
    "m83upi": "<h2>[location], [meta_region_code] Heavy Duty Towing Services You Can Trust</h2>"
})

add_field("aifese", "heavy-img-2", {
    "sq4db": replace_state_shortcodes(create_wp_image("[xfield_company-name]-heavy-tow-truck-[location]-[meta_region_code].jpg", "[xfield_heavy-keyword] Tow Truck [location] AL", "heavy")),
    "24nwxr": replace_state_shortcodes(create_wp_image("[xfield_company-name]-heavy-recovery-[location]-[meta_region_code].jpg", "[xfield_heavy-keyword] Recovery Service [location] AL", "heavy")),
    "2bguwo": replace_state_shortcodes(create_wp_image("[xfield_company-name]-truck-towing-[location]-[meta_region_code].jpg", "Truck [xfield_heavy-keyword] Service [location] AL", "heavy")),
    "42hwv": replace_state_shortcodes(create_wp_image("[xfield_company-name]-heavy-haul-[location]-[meta_region_code].jpg", "[xfield_heavy-keyword] Haul Towing [location] AL", "heavy"))
})

heavy_p3 = get_paragraphs_by_section('heavy', 2)
add_field("matbz", "heavy-paragraph-3", {
    "30etu0j": heavy_p3["version1"],
    "uhkrxs": heavy_p3["version2"],
    "a2hz5n": heavy_p3["version3"],
    "12beqh": heavy_p3["version4"]
})

heavy_p4 = get_paragraphs_by_section('heavy', 3)
add_field("dqke2", "heavy-paragraph-4", {
    "jn80er": heavy_p4["version1"],
    "5cufpn": heavy_p4["version2"],
    "bss3r": heavy_p4["version3"],
    "bt8hn6": heavy_p4["version4"]
})

add_field("ej5zk", "heavy-h2-3", {
    "21wavl": "<h2>Heavy Duty Towing Near Me in [location], [meta_region_code]</h2>"
})

# HEAVY UL with proper structure (next 80 UL items)
heavy_start = 80
heavy_items = processed_ul_items[heavy_start:heavy_start+80] if len(processed_ul_items) > heavy_start else processed_ul_items[heavy_start:]
add_field("2runon", "heavy-ul", create_ul_block(heavy_items))

add_field("9gy7jf", "heavy-btn", {
    "fx1lq": f"GET HEAVY DUTY TOWING IN [location], {meta_title_state} NOW",
    "tis9sj": f"GET HEAVY DUTY TOWING NEAR ME IN [location], {meta_title_state} NOW"
})

# Since heavy versions only have 5 paragraphs (0-4), use paragraph 4 for both 5 and 6
heavy_p5 = get_paragraphs_by_section('heavy', 4)
add_field("wmh9y", "heavy-paragraph-5", {
    "eyn08k": heavy_p5["version1"],
    "tx9eio": heavy_p5["version2"],
    "ffe3cb": heavy_p5["version3"],
    "7mzgzu": heavy_p5["version4"]
})

# For paragraph 6, use paragraph 4 again (since there's no paragraph 5)
heavy_p6 = get_paragraphs_by_section('heavy', 4)
add_field("et1rzl", "heavy-paragraph-6", {
    "lgvh2": heavy_p6["version1"],
    "o5011": heavy_p6["version2"],
    "oouf6v": heavy_p6["version3"],
    "t1qp7r": heavy_p6["version4"]
})

# EQUIPMENT SECTION
add_field("xqmzb", "equipment-meta-title", {
    "tisq38": f"24/7 Heavy Equipment Towing in [location], {meta_title_state} | [xfield_company-name]"
})

add_field("9eh081", "equipment-meta-desc", {
    "wrmeis": "[xfield_company-name] provides 24/7 heavy equipment towing and heavy machinery towing in [location]."
})

add_field("5dnz3", "equipment-h1", {
    "uj26t": "<h1>24/7 Heavy Equipment Towing in [location], [meta_region_code]</h1>"
})

add_field("p14vgo", "equipment-h2-1", {
    "vq96": "<h2>[location], [meta_region_code] Heavy Equipment & Machinery Towing Service</h2>"
})

add_field("bguzaa", "equipment-img-1", {
    "qgt4gn": replace_state_shortcodes(create_wp_image("[xfield_company-name]-heavy-equipment-towing-[location]-[meta_region_code].jpg", "[xfield_equipment-keyword] Equipment Towing [location] AL", "equipment")),
    "6sk5sh": replace_state_shortcodes(create_wp_image("[xfield_company-name]-machinery-transport-[location]-[meta_region_code].jpg", "[xfield_equipment-keyword] Machinery Transport [location] AL", "equipment"))
})

# Get equipment paragraphs using helper function
equipment_p1 = get_paragraphs_by_section('equipment', 0)
add_field("msa63f", "equipment-paragraph-1", {
    "vo9f1": equipment_p1["version1"],
    "7sjrl": equipment_p1["version2"],
    "i2om2t": equipment_p1["version3"],
    "4adix": equipment_p1["version4"]
})

equipment_p2 = get_paragraphs_by_section('equipment', 1)
add_field("qh3mqq", "equipment-paragraph-2", {
    "pzb65a": equipment_p2["version1"],
    "fq17l": equipment_p2["version2"],
    "k3dbi": equipment_p2["version3"],
    "0fte3": equipment_p2["version4"]
})

add_field("0q16o", "equipment-h2-2", {
    "7vnrdm": "<h2>Heavy Equipment Hauling Near Me in [location], [meta_region_code]</h2>"
})

add_field("niil7", "equipment-img-2", {
    "l3zslj": replace_state_shortcodes(create_wp_image("[xfield_company-name]-equipment-hauling-[location]-[meta_region_code].jpg", "[xfield_equipment-keyword] Hauling [location] AL", "equipment")),
    "73k7sd": replace_state_shortcodes(create_wp_image("[xfield_company-name]-construction-equipment-towing-[location]-[meta_region_code].jpg", "Construction [xfield_equipment-keyword] Towing [location] AL", "equipment"))
})

equipment_p3 = get_paragraphs_by_section('equipment', 2)
add_field("dmaz9b", "equipment-paragraph-3", {
    "krgp86": equipment_p3["version1"],
    "ghffwc": equipment_p3["version2"],
    "m8zmf7": equipment_p3["version3"],
    "a86h8j": equipment_p3["version4"]
})

equipment_p4 = get_paragraphs_by_section('equipment', 3)
add_field("ryze2", "equipment-paragraph-4", {
    "j389re": equipment_p4["version1"],
    "d9067": equipment_p4["version2"],
    "ojjjm": equipment_p4["version3"],
    "mnrvn": equipment_p4["version4"]
})

# EQUIPMENT UL with proper structure (next 70 UL items)
equipment_start = 160
equipment_items = processed_ul_items[equipment_start:equipment_start+70] if len(processed_ul_items) > equipment_start else processed_ul_items[equipment_start:]
add_field("febl7d", "equipment-ul", create_ul_block(equipment_items))

add_field("5c6d9t", "equipment-btn", {
    "ox60g8": f"GET [location], {meta_title_state} HEAVY EQUIPMENT TOWING NOW"
})

add_field("b4hwgn", "equipment-h2-3", {
    "3z6t4e": f"<h2>Get Professional Heavy Equipment Towing in [location], {meta_title_state}</h2>",
    "yydta": f"<h2>Heavy Equipment Hauling Near Me in [location], {meta_title_state}</h2>"
})

equipment_p5 = get_paragraphs_by_section('equipment', 4)
add_field("t87nie", "equipment-paragraph-5", {
    "b8tlni": equipment_p5["version1"],
    "b2fj7j": equipment_p5["version2"],
    "65j5nw": equipment_p5["version3"],
    "9b94u": equipment_p5["version4"]
})

equipment_p6 = get_paragraphs_by_section('equipment', 5)
add_field("14qiq", "equipment-paragraph-6", {
    "8i83tm": equipment_p6["version1"],
    "l8tccn": equipment_p6["version2"],
    "nel29c": equipment_p6["version3"],
    "tpd17": equipment_p6["version4"]
})

# TOWING SECTION
add_field("bbih6j", "towing-meta-title", {
    "mlvcx": f"24/7 Towing Company in [location], {meta_title_state} | Tow Truck Near Me"
})

add_field("b8xipc", "towing-meta-desc", {
    "q5k557": "[xfield_company-name] provides 24/7 emergency towing services in [location]. Call for a quick tow truck near me by a trusted towing company."
})

add_field("8byy4", "towing-h1", {
    "1wm5sc": "<h1>24/7 Towing Services in [location], [meta_region_code]</h1>"
})

add_field("xvtkuw", "towing-h2-1", {
    "w2hfeu": "<h2>Reliable Towing Services in [location], [meta_region_code]</h2>"
})

add_field("e84yns", "towing-img-1", {
    "yndpz": replace_state_shortcodes(create_wp_image("[xfield_company-name]-tow-truck-[location]-[meta_region_code].jpg", "[xfield_towing-keyword] Truck Service [location] AL", "towing")),
    "9dcnvc": replace_state_shortcodes(create_wp_image("[xfield_company-name]-emergency-towing-[location]-[meta_region_code].jpg", "Emergency [xfield_towing-keyword] [location] AL", "towing")),
    "0o5bhj": replace_state_shortcodes(create_wp_image("[xfield_company-name]-flatbed-towing-[location]-[meta_region_code].jpg", "Flatbed [xfield_towing-keyword] [location] AL", "towing")),
    "4hmfo": replace_state_shortcodes(create_wp_image("[xfield_company-name]-car-towing-[location]-[meta_region_code].jpg", "Car [xfield_towing-keyword] Service [location] AL", "towing"))
})

# Get towing paragraphs using helper function
towing_p1 = get_paragraphs_by_section('towing', 0)
add_field("vxkind", "towing-paragraph-1", {
    "ewqkze": towing_p1["version1"],
    "9nqx6t": towing_p1["version2"],
    "0qnoz": towing_p1["version3"],
    "z1mrc": towing_p1["version4"]
})

towing_p2 = get_paragraphs_by_section('towing', 1)
add_field("06sn8r", "towing-paragraph-2", {
    "rfz8aa": towing_p2["version1"],
    "yzuxfy": towing_p2["version2"],
    "m1r9d": towing_p2["version3"],
    "zbmam": towing_p2["version4"]
})

add_field("dk4z9t", "towing-h2-2", {
    "g8cl8": "<h2>[location], [meta_region_code]'s #1 Towing Company</h2>"
})

add_field("3rilxj", "towing-img-2", {
    "nle75": replace_state_shortcodes(create_wp_image("[xfield_company-name]-local-towing-[location]-[meta_region_code].jpg", "Local [xfield_towing-keyword] Company [location] AL", "towing")),
    "sqaksd": replace_state_shortcodes(create_wp_image("[xfield_company-name]-wrecker-service-[location]-[meta_region_code].jpg", "Wrecker [xfield_towing-keyword] Service [location] AL", "towing")),
    "6q8eek": replace_state_shortcodes(create_wp_image("[xfield_company-name]-auto-towing-[location]-[meta_region_code].jpg", "Auto [xfield_towing-keyword] [location] AL", "towing")),
    "nb42a1": replace_state_shortcodes(create_wp_image("[xfield_company-name]-vehicle-recovery-[location]-[meta_region_code].jpg", "Vehicle [xfield_towing-keyword] Recovery [location] AL", "towing"))
})

towing_p3 = get_paragraphs_by_section('towing', 2)
add_field("6x8ojn", "towing-paragraph-3", {
    "31v258": towing_p3["version1"],
    "56cvdh": towing_p3["version2"],
    "l47dco": towing_p3["version3"],
    "kvpz4l": towing_p3["version4"]
})

towing_p4 = get_paragraphs_by_section('towing', 3)
add_field("fn3cy", "towing-paragraph-4", {
    "wfqzqh": towing_p4["version1"],
    "xc9e1": towing_p4["version2"],
    "71o2ze": towing_p4["version3"],
    "2bhosg": towing_p4["version4"]
})

add_field("bz4il", "towing-h2-3", {
    "wq0gnm": "<h2>Quick Tow Truck Services Near Me in [location], [meta_region_code]</h2>"
})

towing_p5 = get_paragraphs_by_section('towing', 4)
add_field("i2j7cm", "towing-paragraph-5", {
    "0jrs7i": towing_p5["version1"],
    "ioti3": towing_p5["version2"],
    "1d9sck": towing_p5["version3"],
    "ssl63": towing_p5["version4"]
})

towing_p6 = get_paragraphs_by_section('towing', 5)
add_field("xmipar", "towing-paragraph-6", {
    "gmtus7": towing_p6["version1"],
    "64a6uo": towing_p6["version2"],
    "hyfh0f": towing_p6["version3"],
    "nibtr": towing_p6["version4"]
})

# TOWING UL with proper structure (remaining UL items)
towing_start = 230
towing_items = processed_ul_items[towing_start:] if len(processed_ul_items) > towing_start else []
add_field("g5jbni", "towing-ul", create_ul_block(towing_items))

add_field("bfwu4e", "towing-btn", {
    "gro1ue": f"Call a tow truck in [location], {meta_title_state}",
    "0of8hm": f"QUICK TOW TRUCK [location], {meta_title_state}!",
    "5yum8": f"Get a tow truck near me in [location], {meta_title_state} NOW!",
    "0z0wc": f"Get a Tow Truck now in [location], {meta_title_state}!"
})

add_field("ge1q2g", "towing-h2-4", {
    "lbt0s8": "<h2>Need a Tow Truck Near Me in [location]?</h2>"
})

add_field("v5q5va", "roadside-h2-3", {
    "67z0iw": "<h2>Your Local [location] Roadside Assistance Company</h2>"
})

print(f"Built complete structure with {len(fields)} fields")

# Post-process all fields to replace state shortcodes if single state
if not use_state_shortcode:
    print("Post-processing: Replacing state shortcodes with actual state name...")
    for field_id, field_data in fields.items():
        options = field_data[b'options']
        for opt_id, opt_content in options.items():
            content = opt_content.decode('utf-8')
            if '[meta_region_code]' in content:
                new_content = content.replace('[meta_region_code]', detected_state)
                options[opt_id] = new_content.encode('utf-8')

# Calculate UL distribution
total_ul_options = 0
for field_id, field_data in fields.items():
    label = field_data[b'label'].decode('utf-8')
    if 'ul' in label:
        ul_count = len(field_data[b'options'])
        total_ul_options += ul_count
        print(f"  {label}: {ul_count} options")

print(f"Total UL options distributed: {total_ul_options}")

# Serialize using phpserialize
try:
    serialized_data = phpserialize.dumps(structure)
    print(f"✅ Serialization successful! ({len(serialized_data)} bytes)")
    
    # Test deserialization
    deserialized = phpserialize.loads(serialized_data)
    print("✅ Deserialization successful!")
    
    # Write to file
    with open('magicpage_import_from_txt.txt', 'wb') as f:
        f.write(serialized_data)
    
    print("✅ File written successfully!")
    print("🚀 READY FOR MPP IMPORT WITH ALL UL CONTENT AND PROPER IMAGES!")
    
except Exception as e:
    print(f"❌ Error: {e}")
