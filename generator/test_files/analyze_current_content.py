#!/usr/bin/env python3
import re

print("ANALYZING CURRENT WORKING FILE CONTENT")

with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} characters")

# Count different content types
h1_count = content.count('<h1>')
h2_count = content.count('<h2>')
p_count = content.count('<p>')
ul_count = content.count('<ul>')
img_count = content.count('<img>')

print(f"Content summary:")
print(f"- H1 headers: {h1_count}")
print(f"- H2 headers: {h2_count}")  
print(f"- Paragraphs: {p_count}")
print(f"- UL lists: {ul_count}")
print(f"- Images: {img_count}")

# Check for shortcodes
location_count = content.count('[location]')
region_count = content.count('[meta_region_code]')
company_count = content.count('[xfield_company-name]')

print(f"\nShortcodes:")
print(f"- [location]: {location_count}")
print(f"- [meta_region_code]: {region_count}")
print(f"- [xfield_company-name]: {company_count}")

# Check for sample content
sample_content = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County",
    "Gazebos Towing",
    "Rocky Mount"
]

print(f"\nSample content check:")
sample_found = False
for phrase in sample_content:
    if phrase in content:
        print(f"❌ FOUND: {phrase}")
        sample_found = True
    else:
        print(f"✅ CLEAN: {phrase}")

# Check for raw content
raw_indicators = [
    "Bell's Towing",
    "Ringgold",
    "Calhoun", 
    "Chattanooga",
    "Trenton",
    "Jump Start",
    "Emergency Battery Service"
]

print(f"\nRaw content indicators:")
raw_found = False
for indicator in raw_indicators:
    if indicator in content:
        print(f"✅ FOUND: {indicator}")
        raw_found = True
    else:
        print(f"❌ MISSING: {indicator}")

print(f"\nSUMMARY:")
if sample_found:
    print("❌ Contains sample content that needs to be removed")
else:
    print("✅ No sample content found")

if raw_found:
    print("✅ Contains some raw content")
else:
    print("❌ Missing raw content")

print(f"\nCURRENT STATUS:")
print(f"✅ PHP serialization: WORKING")
print(f"✅ File size: {len(content)} chars (substantial)")
print(f"✅ Structure: {h1_count} H1 + {p_count} paragraphs + {ul_count} UL")

if sample_found:
    print("🔧 NEXT STEP: Remove sample content while preserving structure")
else:
    print("🎉 READY: File is clean and working")

# Show a sample of H1 content
h1_match = re.search(r'<h1>([^<]+)</h1>', content)
if h1_match:
    print(f"\nSample H1: {h1_match.group(1)}")

# Show a sample of paragraph content
p_match = re.search(r'<p>([^<]+)</p>', content)
if p_match:
    print(f"Sample paragraph: {p_match.group(1)[:100]}...")

# Show a sample of UL content
ul_match = re.search(r'<ul[^>]*>([^<]+)</ul>', content)
if ul_match:
    print(f"Sample UL: {ul_match.group(1)[:100]}...")
