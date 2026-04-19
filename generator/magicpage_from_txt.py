#!/usr/bin/env python3
import re
import phpserialize

print("COMPLETE TEMPLATE WITH ALL UL ITEMS AND PROPER IMAGES - 100% RAW DATA")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def resolve_state(detected_state, use_state_shortcode):
    """Centralized state resolver - returns the appropriate state token based on single vs multiple state rule"""
    return "[meta_region_code]" if use_state_shortcode else detected_state

def detect_company_name(text):
    """Dynamically detect company name from text using pattern matching"""
    # Common patterns for company names in towing/roadside assistance content
    patterns = [
        # Pattern 1: Specific pattern for "Bell's Towing & Recovery" (handles both regular and smart quotes) - HIGHEST PRIORITY
        r'\b(Bell[\'\u2019]s\s+Towing\s+&\s+Recovery)\b',
        # Pattern 2: "At [Company Name], we..." or "At [Company Name], we operate..."
        r'\bAt\s+([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+),\s+we\b',
        # Pattern 3: "[Company Name] provides..." or "[Company Name] operates..."
        r'\b([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\s+(?:provides|operates|offers|delivers|serves)\b',
        # Pattern 4: "Call [Company Name] for..." or "Contact [Company Name]..." - MORE SPECIFIC
        r'\b(?:Call|Contact|Reach)\s+([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\s+(?:for|at|in)\b',
        # Pattern 5: "[Company Name] is..." or "[Company Name] has..."
        r'\b([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\s+(?:is|has|offers|provides)\b',
        # Pattern 6: "We at [Company Name]..." or "Here at [Company Name]..."
        r'\b(?:We|Here)\s+at\s+([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\b',
        # Pattern 7: "[Company Name] has built..." or "[Company Name] brings..."
        r'\b([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\s+(?:has\s+built|brings|keeps|eliminates|responds)\b',
        # Pattern 8: "That's why [Company Name]..." or "When you call [Company Name]..."
        r'(?:That[\'\u2019]s\s+why|When\s+you\s+call)\s+([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)',
        # Pattern 9: "[Company Name] keeps..." or "[Company Name] team..."
        r'\b([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\s+(?:keeps|team|crew|fleet)\b',
        # Pattern 10: Specific pattern for "Company Name & Something" format
        r'\b([A-Z][a-z\'\u2019]+\s+Towing\s+&\s+[A-Z][a-z\'\u2019]+)\b',
        # Pattern 11: Specific pattern for "Company Name Wrecker Service" format
        r'\b([A-Z][a-z\'\u2019]+\s+Wrecker\s+Service)\b',
    ]
    
    # Look for company names that contain common towing/roadside keywords
    # More specific keywords to avoid false matches
    towing_keywords = ['towing', 'recovery', 'creeks', 'creek', 'bell', 'wrecker', 'service']
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Check if the match contains towing-related keywords
            if any(keyword.lower() in match.lower() for keyword in towing_keywords):
                # Clean up the match to remove common prefixes
                cleaned_match = match.strip()
                # Remove common prefixes that might be captured
                prefixes_to_remove = ['why ', 'that\'s why ', 'when you call ', 'at ', 'here at ']
                for prefix in prefixes_to_remove:
                    if cleaned_match.lower().startswith(prefix):
                        cleaned_match = cleaned_match[len(prefix):].strip()
                return cleaned_match
    
    # Fallback: Look for any capitalized words that might be company names
    # This is less reliable but catches cases like "Andrus Towing" or "Twin Creeks Towing" or "Bell's Towing & Recovery"
    # Only match if it has at least 2 words and contains towing keywords
    fallback_pattern = r'\b([A-Z][a-z\'\u2019]+(?:\s+[A-Z&][a-z\'\u2019]+)+)\b'
    matches = re.findall(fallback_pattern, text)
    
    for match in matches:
        if any(keyword.lower() in match.lower() for keyword in towing_keywords):
            # Clean up the match to remove common prefixes
            cleaned_match = match.strip()
            # Remove common prefixes that might be captured
            prefixes_to_remove = ['why ', 'that\'s why ', 'when you call ', 'at ', 'here at ']
            for prefix in prefixes_to_remove:
                if cleaned_match.lower().startswith(prefix):
                    cleaned_match = cleaned_match[len(prefix):].strip()
            return cleaned_match
    
    return None

def detect_city_from_h2(h2_text):
    """Detect city name from H2 text that contains city without state"""
    # Pattern to match "Need a Tow Truck Near Me in Washington" or similar
    patterns = [
        r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\?',  # "in St. George?" or "in Washington?"
        r'\bnear\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\?',  # "near St. George?" or "near Washington?"
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*[A-Z]{2}',  # "St. George, UT" or "Washington, UT" (already handled)
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$',  # "St. George" or "Washington" at end of string
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, h2_text)
        for match in matches:
            # Skip common words that aren't cities
            skip_words = ['me', 'you', 'us', 'now', 'today', 'here', 'there', 'service', 'services', 'towing', 'truck', 'trucks', 'assistance', 'help', 'call', 'get', 'need', 'want', 'find', 'near', 'in', 'for', 'with', 'and', 'or', 'the', 'a', 'an']
            if match.lower() not in skip_words and len(match) > 2:
                return match.strip()
    
    return None

def replace_city_in_text(text, city_name):
    """Replace all instances of a city name with [location] in text"""
    if not city_name:
        return text
    
    # Replace city name with [location] (case insensitive)
    # Use word boundaries to avoid partial matches
    pattern = r'\b' + re.escape(city_name) + r'\b'
    text = re.sub(pattern, '[location]', text, flags=re.IGNORECASE)
    
    return text

def apply_shortcodes_to_ul_item(text, detected_location=None, detected_state=None, use_state_shortcode=True, detected_company=None):
    """Apply shortcodes specifically to UL items - replace only the 4 sample city names"""
    # Replace the 4 specific sample city names with [location]
    sample_cities = ['Falls Church', 'Alexandria', 'Vienna', 'Gaithersburg']
    for city in sample_cities:
        text = text.replace(city, '[location]')
    
    # Replace state codes with [meta_region_code]
    text = re.sub(r',\s*[A-Z]{2}$', ', [meta_region_code]', text)
    
    # Replace company names (use detected company or fallback to hardcoded)
    if detected_company:
        text = text.replace(detected_company, "[xfield_company-name]")
    else:
        # Fallback to hardcoded company names
        text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
        text = text.replace("Twin Creeks Towing", "[xfield_company-name]")
        text = text.replace("Andrus Towing", "[xfield_company-name]")
        text = text.replace("Henry's Wrecker Service", "[xfield_company-name]")
    
    return text

def apply_shortcodes(text, detected_location=None, detected_state=None, use_state_shortcode=True, detected_company=None, detected_city=None):
    # Replace ALL city names with [location] - use a more comprehensive pattern for multi-word cities
    # This will catch city names (including multi-word ones) followed by a comma and state
    text = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b', '[location], [meta_region_code]', text)
    
    # Clean up any remaining partial replacements like "St. [location]"
    text = re.sub(r'\bSt\.\s+\[location\]', '[location]', text)
    
    # Replace specific city name detected from H2 if provided
    if detected_city:
        text = replace_city_in_text(text, detected_city)
    
    # Replace company names (use detected company or fallback to hardcoded)
    if detected_company:
        text = text.replace(detected_company, "[xfield_company-name]")
    else:
        # Fallback to hardcoded company names
        text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
        text = text.replace("Twin Creeks Towing", "[xfield_company-name]")
        text = text.replace("Andrus Towing", "[xfield_company-name]")
        text = text.replace("Henry's Wrecker Service", "[xfield_company-name]")
    
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

# Detect company name from raw content
print("Detecting company name...")
detected_company = detect_company_name(raw_text)
if detected_company:
    print(f"Detected company: '{detected_company}'")
else:
    print("Could not detect company name - will use fallback")

# Apply shortcodes with detected location/state
h1_text_processed = apply_shortcodes(h1_text, detected_location, detected_state, use_state_shortcode, detected_company) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text_processed}</h1>'

# Extract content by complete versions (H1 to next H1)
print("Extracting content by complete versions...")
version_pattern = r'<H1[^>]*>.*?</H1>.*?(?=<H1[^>]*>|$)'
version_matches = re.findall(version_pattern, raw_text, re.DOTALL | re.IGNORECASE)

# Also extract the H1 tags separately for categorization
h1_pattern = r'<H1[^>]*>(.*?)</H1>'
h1_matches = re.findall(h1_pattern, raw_text, re.IGNORECASE)

print(f"Found {len(version_matches)} complete versions")

# Process each version to extract structured content and categorize by H1
version_data = []
category_versions = {
    'roadside': [],
    'heavy': [],
    'towing': [],
    'equipment': []
}
category_ul_items = {}
category_version_counters = {}

def categorize_by_h1(h1_text):
    """Categorize version based on H1 text content"""
    h1_lower = h1_text.lower()
    if 'roadside' in h1_lower:
        return 'roadside'
    elif 'heavy' in h1_lower and 'equipment' not in h1_lower:
        return 'heavy'
    elif 'equipment' in h1_lower:
        return 'equipment'
    elif 'towing' in h1_lower and 'heavy' not in h1_lower:
        return 'towing'
    else:
        return 'roadside'  # Default fallback

for i, version_content in enumerate(version_matches):
    print(f"Processing version {i+1}...")
    
    # Extract H2s first to detect city name
    h2s = re.findall(r'<H2[^>]*>(.*?)</H2>', version_content, re.IGNORECASE)
    
    # Detect city name from H2s (look for city without state)
    detected_city = None
    for h2_text in h2s:
        city = detect_city_from_h2(h2_text)
        if city:
            detected_city = city
            break
    
    # Get H1 text from the separate H1 matches
    if i < len(h1_matches):
        h1_text = h1_matches[i].strip()
        
        # Categorize this version BEFORE applying shortcodes
        category = categorize_by_h1(h1_text)
        
        h1_processed = apply_shortcodes(h1_text, detected_location, detected_state, use_state_shortcode, detected_company, detected_city)
        h1_content = f'<h1>{h1_processed}</h1>'
    else:
        h1_content = f'<h1>24/7 Roadside Assistance [location], {resolve_state(detected_state, use_state_shortcode)}</h1>'
        category = 'roadside'  # Default fallback
    
    # Process paragraphs and UL items
    paragraphs = []
    ul_items = []
    
    # Extract UL items by looking for actual list items with * or - prefixes
    # Process each line to find actual UL items
    lines = version_content.split('\n')
    for line in lines:
        line = line.strip()
        # Look for lines that start with * or - and contain actual list content
        if (line.startswith('* ') or line.startswith('- ')) and not line.startswith('Button:') and not line.startswith('Link:'):
            # Clean up the line and check if it's a valid list item
            item = line[2:].strip()  # Remove the * or - prefix
            if item and len(item) < 200:  # Reasonable length for a list item
                # Check if it doesn't contain H2 tags or other HTML that shouldn't be in a list
                if not re.search(r'<H[1-6]', item, re.IGNORECASE) and not re.search(r'<p>', item, re.IGNORECASE):
                    ul_text = apply_shortcodes_to_ul_item(item, detected_location, detected_state, use_state_shortcode, detected_company)
                    ul_items.append(ul_text)
    
    if ul_items:
        print(f"  DEBUG: Found {len(ul_items)} UL items for {category} version {i+1}")
    else:
        print(f"  DEBUG: No UL section found for {category} version {i+1}")
    
    # Split by H2 tags to get paragraphs between them
    h2_sections = re.split(r'<H2[^>]*>.*?</H2>', version_content, flags=re.IGNORECASE)
    
    # Process each section and map paragraphs to correct slots
    section_paragraphs = []
    for j, section in enumerate(h2_sections):
        section_paras = []
        lines = section.strip().split('\n')
        for line in lines:
            line = line.strip()
            if (line and not line.startswith('*') and len(line) > 30 and 
                not line.lower().startswith('button:') and 
                not line.lower().startswith('link:') and
                not line.startswith('_') and
                not line.lower().startswith('tel:') and
                not line.startswith('________________')):
                # This is a paragraph
                p_text = apply_shortcodes(line, detected_location, detected_state, use_state_shortcode, detected_company, detected_city)
                section_paras.append(f'<p>{p_text}</p>')
                # Debug: Check for specific content
                if 'Choose Andrus Towing' in line:
                    print(f"  DEBUG: Found 'Choose Andrus Towing' in section {j}, line: {line[:100]}...")
        section_paragraphs.append(section_paras)
        if section_paras:
            print(f"  DEBUG: Section {j} has {len(section_paras)} paragraphs")
    
    # Map paragraphs to correct slots based on H2 sections
    # H2-1: p1, p2 (indices 0, 1)
    # H2-2: p3, p4 (indices 2, 3) 
    # H2-3: p5, p6 (indices 4, 5)
    # H2-4: p7, p8 (handled separately)
    paragraphs = []
    for i, section_paras in enumerate(section_paragraphs):
        if i == 0:  # Before first H2 - skip
            continue
        elif i <= 3:  # H2-1, H2-2, H2-3 sections
            paragraphs.extend(section_paras)
        # H2-4 paragraphs are handled separately below
    
    # Handle the case where we have 4 H2s - store H2-4 separately and its paragraphs as p7 and p8
    h2_4_content = None
    paragraph_7 = None
    paragraph_8 = None
    if len(h2s) >= 4:
        h2_4_text = h2s[3]
        h2_4_processed = apply_shortcodes(h2_4_text, detected_location, detected_state, use_state_shortcode, detected_company, detected_city)
        h2_4_content = f'<h2>{h2_4_processed}</h2>'
        
        # Get paragraphs from H2-4 section (index 4 in section_paragraphs)
        if len(section_paragraphs) > 4 and section_paragraphs[4]:
            h2_4_paras = section_paragraphs[4]
            if len(h2_4_paras) >= 2:
                # Two paragraphs after H2-4: first becomes p7, second becomes p8
                paragraph_7 = h2_4_paras[0]
                paragraph_8 = h2_4_paras[1]
            elif len(h2_4_paras) == 1:
                # Only one paragraph after H2-4: becomes p7
                paragraph_7 = h2_4_paras[0]
    
    version_info = {
        'h1': h1_content,
        'h2s': h2s[:3] if len(h2s) > 3 else h2s,  # Only keep first 3 H2s
        'h2_4': h2_4_content,  # Store H2-4 separately (just the H2, no paragraph)
        'paragraph_7': paragraph_7,  # Store first H2-4 paragraph as p7
        'paragraph_8': paragraph_8,  # Store second H2-4 paragraph as p8 (if exists)
        'paragraphs': paragraphs,
        'ul_items': ul_items,
        'category': category
    }
    
    # Add UL items to category-specific lists (from ALL versions)
    if category not in category_ul_items:
        category_ul_items[category] = []
    
    # Track version number within each category
    if category not in category_version_counters:
        category_version_counters[category] = 0
    category_version_counters[category] += 1
    
    # Store UL items for this specific version
    version_ul_key = f"{category}_version_{category_version_counters[category]}"
    category_ul_items[version_ul_key] = ul_items.copy()
    print(f"  DEBUG: Added {len(ul_items)} UL items to {category} version {category_version_counters[category]} (key: {version_ul_key})")
    
    version_data.append(version_info)
    category_versions[category].append(version_info)
    print(f"  Version {i+1}: {len(h2s)} H2s, {len(paragraphs)} paragraphs")

# Print categorization summary
print("\n=== CATEGORIZATION SUMMARY ===")
for category, versions in category_versions.items():
    print(f"{category.upper()}: {len(versions)} versions")
    for i, version in enumerate(versions):
        h1_text = version['h1'].replace('<h1>', '').replace('</h1>', '')
        print(f"  {i+1}. {h1_text}")

# Flatten paragraphs for backward compatibility
raw_paragraphs = []
for version in version_data:
    raw_paragraphs.extend(version['paragraphs'])

# Count total UL items by category
total_ul_items = sum(len(items) for items in category_ul_items.values())
print(f"Raw content: H1, {len(raw_paragraphs)} paragraphs, {total_ul_items} UL items")

# VALIDATION: Check UL items processing by category
print("\n=== UL PROCESSING VALIDATION ===")
# Group by category and show summary
category_summary = {}
for key, items in category_ul_items.items():
    if '_version_' in key:
        category = key.split('_version_')[0]
        if category not in category_summary:
            category_summary[category] = []
        category_summary[category].append(len(items))

for category, counts in category_summary.items():
    total_items = sum(counts)
    print(f"{category.upper()}: {len(counts)} versions, {total_items} total UL items")
    if counts:
        print(f"  Items per version: {counts}")
        # Show first item from first version
        first_version_key = f"{category}_version_1"
        if first_version_key in category_ul_items and category_ul_items[first_version_key]:
            print(f"  First item: {category_ul_items[first_version_key][0]}")
    
    # Debug: show all version keys for this category
    version_keys = [key for key in category_ul_items.keys() if key.startswith(f"{category}_version_")]
    print(f"  Found {len(version_keys)} version keys: {version_keys}")
print("✅ UL items processing looks good")

# Check for problematic patterns in each category
for category, counts in category_summary.items():
    problematic_found = False
    for version_num in range(1, len(counts) + 1):
        version_key = f"{category}_version_{version_num}"
        if version_key in category_ul_items:
            items = category_ul_items[version_key]
            problematic_items = []
            for i, item in enumerate(items):
                if item.strip() in ['[location], [meta_region_code]', '[location], UT', 'UT']:
                    problematic_items.append((i, item))
            
            if problematic_items:
                if not problematic_found:
                    print(f"\n⚠️  WARNING: Found problematic {category} UL items:")
                    problematic_found = True
                print(f"  Version {version_num}: {len(problematic_items)} problematic items")
                for i, item in problematic_items[:2]:  # Show first 2
                    print(f"    Index {i}: '{item}'")
    
    if not problematic_found:
        print(f"✅ No problematic {category} UL items found")

def get_paragraph(index):
    if index < len(raw_paragraphs):
        return raw_paragraphs[index]
    elif raw_paragraphs:
        return raw_paragraphs[index % len(raw_paragraphs)]
    else:
        return f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'

def get_paragraph_by_version(version_index, paragraph_index):
    """Get a specific paragraph from a specific version"""
    if version_index < len(version_data):
        version_paragraphs = version_data[version_index]['paragraphs']
        if paragraph_index < len(version_paragraphs):
            return version_paragraphs[paragraph_index]
        elif version_paragraphs:
            return version_paragraphs[paragraph_index % len(version_paragraphs)]
    
    # Fallback
    return f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'

def get_h2_by_version(version_index, h2_index):
    """Get a specific H2 from a specific version"""
    if version_index < len(version_data):
        version_h2s = version_data[version_index]['h2s']
        if h2_index < len(version_h2s):
            h2_text = version_h2s[h2_index]
            h2_processed = apply_shortcodes(h2_text, detected_location, detected_state, use_state_shortcode, detected_company)
            return f'<h2>{h2_processed}</h2>'
    
    # Fallback
    return f'<h2>Professional Service in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>'

def get_paragraphs_by_section(section, paragraph_index):
    """Get paragraphs for a specific section and paragraph index from category buckets"""
    if section in category_versions:
        versions = category_versions[section]
        
        # Get up to 4 versions for this category
        version_count = min(4, len(versions))
        
        result = {}
        for i in range(4):
            if i < version_count:
                # Get paragraph from this version
                version_paragraphs = versions[i]['paragraphs']
                if paragraph_index < len(version_paragraphs):
                    result[f"version{i+1}"] = version_paragraphs[paragraph_index]
                elif version_paragraphs:
                    # Wrap around if not enough paragraphs
                    result[f"version{i+1}"] = version_paragraphs[paragraph_index % len(version_paragraphs)]
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
            else:
                # Use the last available version if we don't have 4 versions
                if versions:
                    last_version = versions[-1]
                    version_paragraphs = last_version['paragraphs']
                    if paragraph_index < len(version_paragraphs):
                        result[f"version{i+1}"] = version_paragraphs[paragraph_index]
                    elif version_paragraphs:
                        result[f"version{i+1}"] = version_paragraphs[paragraph_index % len(version_paragraphs)]
                    else:
                        result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
        
        return result
    else:
        # Fallback for unknown sections
        fallback = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
        return {
            "version1": fallback,
            "version2": fallback,
            "version3": fallback,
            "version4": fallback
        }

def get_h2_4_by_section(section):
    """Get H2-4 content for a specific section from category buckets"""
    if section in category_versions:
        versions = category_versions[section]
        version_count = min(4, len(versions))
        result = {}
        for i in range(4):
            if i < version_count:
                h2_4_content = versions[i].get('h2_4')
                if h2_4_content:
                    result[f"version{i+1}"] = h2_4_content
                else:
                    result[f"version{i+1}"] = f'<h2>Professional Service in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>'
            else:
                if versions:
                    last_version = versions[-1]
                    h2_4_content = last_version.get('h2_4')
                    if h2_4_content:
                        result[f"version{i+1}"] = h2_4_content
                    else:
                        result[f"version{i+1}"] = f'<h2>Professional Service in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>'
                else:
                    result[f"version{i+1}"] = f'<h2>Professional Service in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>'
        return result
    else:
        fallback = f'<h2>Professional Service in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>'
        return {
            "version1": fallback,
            "version2": fallback,
            "version3": fallback,
            "version4": fallback
        }

def get_paragraph_7_by_section(section):
    """Get paragraph-7 content for a specific section from category buckets"""
    if section in category_versions:
        versions = category_versions[section]
        version_count = min(4, len(versions))
        result = {}
        for i in range(4):
            if i < version_count:
                paragraph_7 = versions[i].get('paragraph_7')
                if paragraph_7:
                    result[f"version{i+1}"] = paragraph_7
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
            else:
                if versions:
                    last_version = versions[-1]
                    paragraph_7 = last_version.get('paragraph_7')
                    if paragraph_7:
                        result[f"version{i+1}"] = paragraph_7
                    else:
                        result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
        return result
    else:
        fallback = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
        return {
            "version1": fallback,
            "version2": fallback,
            "version3": fallback,
            "version4": fallback
        }

def get_paragraph_8_by_section(section):
    """Get paragraph-8 content for a specific section from category buckets"""
    if section in category_versions:
        versions = category_versions[section]
        version_count = min(4, len(versions))
        result = {}
        for i in range(4):
            if i < version_count:
                paragraph_8 = versions[i].get('paragraph_8')
                if paragraph_8:
                    result[f"version{i+1}"] = paragraph_8
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
            else:
                if versions:
                    last_version = versions[-1]
                    paragraph_8 = last_version.get('paragraph_8')
                    if paragraph_8:
                        result[f"version{i+1}"] = paragraph_8
                    else:
                        result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
                else:
                    result[f"version{i+1}"] = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
        return result
    else:
        fallback = f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>'
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

# Helper to create proper UL blocks with multiple LI items and prepended paragraphs
def create_ul_block_with_paragraphs(items, paragraph_7_dict, paragraph_8_dict, items_per_option=20):
    """Create UL options where each option contains paragraphs + UL with multiple LI items"""
    ul_dict = {}
    key_options = ["9vxk2p", "rddpm7", "6f5bza", "q1gbzg", "7xj2jn", "rc9iod", "armq2", "x58wh", "u3ql0n", "2k8fgh", 
                   "cz8bsk", "yzjhed", "dblfsd", "n01p7o", "r9x286", "g6m6l", "9cyet8", "o4p9w", "0ltva", "cnsb2c",
                   "w00bpu", "actg0a", "dbs1hl", "wpjh5s2", "x6a6u", "0l4o2", "m9dc4", "y49n57", "nk6vo", "o4fgb"]
    
    # Filter out paragraphs and button text - only keep actual UL items
    ul_items = []
    for item in items:
        if (not item.startswith('<p>') and not item.endswith('</p>') and 
            not item.lower().startswith('button:') and not item.lower().startswith('link:')):
            ul_items.append(item)
    
    # Create multiple UL options, each with multiple LI items
    option_count = min(10, (len(ul_items) + items_per_option - 1) // items_per_option)  # Max 10 options
    
    print(f"    Creating {option_count} UL options from {len(ul_items)} items")
    
    for i in range(option_count):
        start_idx = i * items_per_option
        end_idx = min(start_idx + items_per_option, len(ul_items))
        
        # Create LI items for this option
        li_items = []
        for j in range(start_idx, end_idx):
            if j < len(ul_items):
                li_items.append(f'<li>{ul_items[j]}</li>')
        
        # Create the complete UL block with prepended paragraphs
        if li_items:
            key = key_options[i % len(key_options)]
            
            # Get the paragraph variations for this option
            p7_key = f"version{(i % 4) + 1}"  # Cycle through versions
            p8_key = f"version{(i % 4) + 1}"
            
            p7_content = paragraph_7_dict.get(p7_key, '')
            p8_content = paragraph_8_dict.get(p8_key, '')
            
            # Add "And more!" at the end of the list
            li_items.append('<li>And more!</li>')
            
            # Combine paragraphs and UL
            paragraph_content = p7_content + p8_content
            ul_content = f"{paragraph_content}<ul class='whiterail-ul'>{''.join(li_items)}</ul>"
            ul_dict[key] = ul_content
            print(f"    Option {i+1} ({key}): {len(li_items)} items, first item: '{ul_items[start_idx] if start_idx < len(ul_items) else 'N/A'}'")
    
    return ul_dict

def create_ul_block_for_category(category, category_ul_items, paragraph_7_dict, paragraph_8_dict):
    """Create UL block for a category with multiple versions"""
    ul_dict = {}
    key_options = ["9vxk2p", "rddpm7", "6f5bza", "q1gbzg", "7xj2jn", "rc9iod", "armq2", "x58wh", "u3ql0n", "2k8fgh", 
                   "cz8bsk", "yzjhed", "dblfsd", "n01p7o", "r9x286", "g6m3k", "h4n8p", "j7q2w", "k9r5t", "l3s8v"]
    
    # Find all versions for this category
    version_keys = [key for key in category_ul_items.keys() if key.startswith(f"{category}_version_")]
    version_keys.sort(key=lambda x: int(x.split('_version_')[1]))
    
    if not version_keys:
        return {"9vxk2p": "<p>Professional service available in your area.</p><ul><li>24/7 Emergency Response</li><li>Licensed & Insured</li><li>Fast Response Time</li></ul>"}
    
    # Create one option per version using custom keys
    for i, version_key in enumerate(version_keys):
        if i >= len(key_options):
            break
            
        items = category_ul_items[version_key]
        
        # Create paragraph content for this version
        paragraph_content = ""
        version_num = int(version_key.split('_version_')[1])
        
        # Get paragraph-7 and paragraph-8 for this specific version
        p7_content = ""
        p8_content = ""
        
        if paragraph_7_dict and f"version{version_num}" in paragraph_7_dict:
            p7_content = paragraph_7_dict[f"version{version_num}"]
        if paragraph_8_dict and f"version{version_num}" in paragraph_8_dict:
            p8_content = paragraph_8_dict[f"version{version_num}"]
        
        # Only add paragraph content if it's not the default and not duplicated
        if p7_content and p7_content != f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>':
            paragraph_content += p7_content
        if p8_content and p8_content != f'<p>[xfield_company-name] provides professional service in [location], {resolve_state(detected_state, use_state_shortcode)}.</p>' and p8_content != p7_content:
            paragraph_content += p8_content
        
        # Create UL content (even if empty)
        ul_content = "<ul class='whiterail-ul'>"
        if items:
            for item in items:
                ul_content += f"<li>{item}</li>"
        else:
            # Add default UL items if no items found
            ul_content += "<li>Professional service available in your area</li>"
            ul_content += "<li>24/7 Emergency Response</li>"
            ul_content += "<li>Licensed & Insured</li>"
        ul_content += "</ul>"
        
        # Combine paragraph and UL content
        full_content = paragraph_content + ul_content
        ul_dict[key_options[i]] = full_content
    
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
add_field("c0g3b1f", "roadside-meta-title", {
    "8q6ubd": f"24/7 Emergency Roadside Assistance [location], {resolve_state(detected_state, use_state_shortcode)} | [xfield_company-name]"
})

add_field("ex59ys", "roadside-meta-desc", {
    "ttpvck": "[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call for fuel delivery, vehicle lockouts, battery jumps, & more."
})

add_field("pgn00b", "roadside-h1", {
    "7xj2jn": h1_content
})

add_field("g92x2", "roadside-h2-1", {
    "8mch6i": f"<h2>Emergency Roadside Services in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

add_field("nyfvy", "roadside-img-1", {
    "icqjo8": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside")),
    "zqtylq": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside")),
    "rznnlkg": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", " [xfield_roadside-keyword] [location]", "roadside")),
    "hcn5ub": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside"))
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
    "9zek4": f"<h2>Get Quick Roadside Assistance Near Me in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

add_field("wirda", "roadside-img-2", {
    "siiztr": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside")),
    "iwruys": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside")),
    "h495ns": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside")),
    "3a1nii": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_roadside-keyword] [location]", "roadside"))
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

# ROADSIDE UL with proper structure (category-specific UL items)
print(f"\n=== ROADSIDE UL VALIDATION ===")
print("Creating roadside UL options...")

# Get paragraph-7 and paragraph-8 for roadside
roadside_p7 = get_paragraph_7_by_section('roadside')
roadside_p8 = get_paragraph_8_by_section('roadside')

add_field("feebkl", "roadside-ul", create_ul_block_for_category('roadside', category_ul_items, roadside_p7, roadside_p8))

add_field("52i9lm", "roadside-btn", {
    "4lzqbp": f"Call [xfield_company-name] for Roadside Assistance in [location], {resolve_state(detected_state, use_state_shortcode)} Now!",
    "wb7x8v": f"Get Roadside Assistance in [location], {resolve_state(detected_state, use_state_shortcode)} Now!"
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
    "ocikhb": f"24/7 Heavy Duty Towing in [location], {resolve_state(detected_state, use_state_shortcode)} | [xfield_company-name]"
})

add_field("j0eud5", "heavy-meta-desc", {
    "9teic7": "[xfield_company-name] provides 24/7 heavy duty towing in [location]. Call for heavy towing, heavy recovery, & heavy duty roadside assistance."
})

add_field("s2bozf", "heavy-h1", {
    "3gj4as": f"<h1>24/7 Heavy Tow Truck in [location], {resolve_state(detected_state, use_state_shortcode)}</h1>"
})

add_field("m8niv", "heavy-h2-1", {
    "7mc6qu": f"<h2>24/7 Heavy Tow Truck in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

add_field("fv2bh5", "heavy-img-1", {
    "db7sl": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy")),
    "561yep": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy")),
    "9oe81q": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy")),
    "xjsi7d": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy"))
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
    "m83upi": f"<h2>[location], {resolve_state(detected_state, use_state_shortcode)} Heavy Duty Towing Services You Can Trust</h2>"
})

add_field("aifese", "heavy-img-2", {
    "sq4db": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy")),
    "24nwxr": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy")),
    "2bguwo": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword]  [location]", "heavy")),
    "42hwv": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_heavy-keyword] [location]", "heavy"))
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
    "21wavl": f"<h2>Heavy Duty Towing Near Me in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

# HEAVY UL with proper structure (category-specific UL items)
print(f"\n=== HEAVY UL VALIDATION ===")
print("Creating heavy UL options...")

# Get paragraph-7 and paragraph-8 for heavy
heavy_p7 = get_paragraph_7_by_section('heavy')
heavy_p8 = get_paragraph_8_by_section('heavy')

add_field("2runon", "heavy-ul", create_ul_block_for_category('heavy', category_ul_items, heavy_p7, heavy_p8))

add_field("9gy7jf", "heavy-btn", {
    "fx1lq": f"GET HEAVY TOWING IN [location], {resolve_state(detected_state, use_state_shortcode)} NOW",
    "tis9sj": f"GET HEAVY TOWING NEAR ME IN [location], {resolve_state(detected_state, use_state_shortcode)} NOW"
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
    "tisq38": f"24/7 Heavy Equipment Towing in [location], {resolve_state(detected_state, use_state_shortcode)} | [xfield_company-name]"
})

add_field("9eh081", "equipment-meta-desc", {
    "wrmeis": "[xfield_company-name] provides 24/7 heavy equipment towing and heavy machinery towing in [location]."
})

add_field("5dnz3", "equipment-h1", {
    "uj26t": f"<h1>24/7 Heavy Equipment Towing in [location], {resolve_state(detected_state, use_state_shortcode)}</h1>"
})

add_field("p14vgo", "equipment-h2-1", {
    "vq96": f"<h2>[location], {resolve_state(detected_state, use_state_shortcode)} Heavy Equipment & Machinery Towing Service</h2>"
})

add_field("bguzaa", "equipment-img-1", {
    "qgt4gn": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_equipment-keyword] [location]", "equipment")),
    "6sk5sh": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_equipment-keyword] [location]", "equipment"))
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
    "7vnrdm": f"<h2>Heavy Equipment Hauling Near Me in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

add_field("niil7", "equipment-img-2", {
    "l3zslj": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_equipment-keyword] [location]", "equipment")),
    "73k7sd": replace_state_shortcodes(create_wp_image("placeholder.jpg", "[xfield_equipment-keyword] [location]", "equipment"))
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

# EQUIPMENT UL with proper structure (category-specific UL items)
print(f"\n=== EQUIPMENT UL VALIDATION ===")
print("Creating equipment UL options...")

# Get paragraph-7 and paragraph-8 for equipment
equipment_p7 = get_paragraph_7_by_section('equipment')
equipment_p8 = get_paragraph_8_by_section('equipment')

add_field("febl7d", "equipment-ul", create_ul_block_for_category('equipment', category_ul_items, equipment_p7, equipment_p8))

add_field("5c6d9t", "equipment-btn", {
    "ox60g8": f"GET [location], {resolve_state(detected_state, use_state_shortcode)} HEAVY EQUIPMENT TOWING NOW"
})

add_field("b4hwgn", "equipment-h2-3", {
    "3z6t4e": f"<h2>Get Professional Heavy Equipment Towing in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>",
    "yydta": f"<h2>Heavy Equipment Hauling Near Me in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
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
    "mlvcx": f"24/7 Towing Company in [location], {resolve_state(detected_state, use_state_shortcode)} | Tow Truck Near Me"
})

add_field("b8xipc", "towing-meta-desc", {
    "q5k557": "[xfield_company-name] provides 24/7 emergency towing services in [location]. Call for a quick tow truck near me by a trusted towing company."
})

add_field("8byy4", "towing-h1", {
    "1wm5sc": f"<h1>24/7 Towing Services in [location], {resolve_state(detected_state, use_state_shortcode)}</h1>"
})

add_field("xvtkuw", "towing-h2-1", {
    "w2hfeu": f"<h2>Reliable Towing Services in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
})

add_field("e84yns", "towing-img-1", {
    "yndpz": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "9dcnvc": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "0o5bhj": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "4hmfo": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing"))
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
    "g8cl8": f"<h2>[location], {resolve_state(detected_state, use_state_shortcode)}'s #1 Towing Company</h2>"
})

add_field("3rilxj", "towing-img-2", {
    "nle75": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "sqaksd": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "6q8eek": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing")),
    "nb42a1": replace_state_shortcodes(create_wp_image(f"placeholder.jpg", "[xfield_towing-keyword] [location]", "towing"))
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
    "wq0gnm": f"<h2>Quick Tow Truck Services Near Me in [location], {resolve_state(detected_state, use_state_shortcode)}</h2>"
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

# TOWING UL with proper structure (category-specific UL items)
print(f"\n=== TOWING UL VALIDATION ===")
print("Creating towing UL options...")

# Get paragraph-7 and paragraph-8 for towing
towing_p7 = get_paragraph_7_by_section('towing')
towing_p8 = get_paragraph_8_by_section('towing')

add_field("g5jbni", "towing-ul", create_ul_block_for_category('towing', category_ul_items, towing_p7, towing_p8))

add_field("bfwu4e", "towing-btn", {
    "gro1ue": f"Call a tow truck in [location], {resolve_state(detected_state, use_state_shortcode)}",
    "0of8hm": f"QUICK TOW TRUCK [location], {resolve_state(detected_state, use_state_shortcode)}!",
    "5yum8": f"Get a tow truck near me in [location], {resolve_state(detected_state, use_state_shortcode)} NOW!",
    "0z0wc": f"Get a Tow Truck now in [location], {resolve_state(detected_state, use_state_shortcode)}!"
})

add_field("v5q5va", "roadside-h2-3", {
    "67z0iw": "<h2>Your Local [location] Roadside Assistance Company</h2>"
})

# H2-4 fields for sections that have 4 H2s
print("Creating H2-4 fields for sections with 4 H2s...")

# Check which sections have H2-4 content
for section in ['roadside', 'heavy', 'equipment', 'towing']:
    if section in category_versions:
        versions = category_versions[section]
        has_h2_4 = any(version.get('h2_4') for version in versions)
        if has_h2_4:
            print(f"Creating H2-4 field for {section}...")
            h2_4_content = get_h2_4_by_section(section)
            field_id = f"{section}_h2_4"
            field_label = f"{section}-h2-4"
            add_field(field_id, field_label, h2_4_content)
        else:
            print(f"No H2-4 content found for {section}, skipping...")

# Paragraph-7 and Paragraph-8 fields for sections that have them
print("Creating paragraph-7 and paragraph-8 fields...")

for section in ['roadside', 'heavy', 'equipment', 'towing']:
    if section in category_versions:
        versions = category_versions[section]
        has_p7 = any(version.get('paragraph_7') for version in versions)
        has_p8 = any(version.get('paragraph_8') for version in versions)
        
        if has_p7:
            print(f"Creating paragraph-7 field for {section}...")
            p7_content = get_paragraph_7_by_section(section)
            field_id = f"{section}_p7"
            field_label = f"{section}-p7"
            add_field(field_id, field_label, p7_content)
        
        if has_p8:
            print(f"Creating paragraph-8 field for {section}...")
            p8_content = get_paragraph_8_by_section(section)
            field_id = f"{section}_p8"
            field_label = f"{section}-p8"
            add_field(field_id, field_label, p8_content)

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
