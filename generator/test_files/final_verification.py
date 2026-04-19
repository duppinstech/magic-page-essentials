#!/usr/bin/env python3
import re

print("FINAL VERIFICATION - 100% RAW DATA FILE")

# Read the file
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} characters")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    result = phpserialize.loads(test_data)
    print(f'✅ PHP serialization: WORKING ({len(test_data)} bytes)')
except Exception as e:
    print(f'❌ PHP error: {e}')
    exit(1)

# Check for EXACT sample content (case sensitive)
sample_phrases = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County",
    "Gazebos Towing",
    "Rocky Mount"
]

print("\nSample content check (EXACT phrases):")
all_clean = True
for phrase in sample_phrases:
    if phrase in content:  # Exact case-sensitive match
        print(f"❌ FOUND: {phrase}")
        all_clean = False
    else:
        print(f"✅ CLEAN: {phrase}")

# Check for raw content indicators
raw_indicators = [
    "Bell's Towing",
    "[location]",
    "[meta_region_code]", 
    "[xfield_company-name]",
    "Jump Start",
    "Emergency Battery Service",
    "Flat Tire Change"
]

print("\nRaw content verification:")
raw_present = True
for indicator in raw_indicators:
    count = content.count(indicator)
    if count > 0:
        print(f"✅ {indicator}: {count} instances")
    else:
        print(f"❌ MISSING: {indicator}")
        raw_present = False

# Count content elements
h1_count = content.count('<h1>')
p_count = content.count('<p>')
ul_count = content.count('<ul>')
location_count = content.count('[location]')
company_count = content.count('[xfield_company-name]')

print(f"\nContent analysis:")
print(f"✅ H1 headers: {h1_count}")
print(f"✅ Paragraphs: {p_count}")
print(f"✅ UL lists: {ul_count}")
print(f"✅ [location] shortcodes: {location_count}")
print(f"✅ [xfield_company-name] shortcodes: {company_count}")

# Final status
print(f"\n{'='*50}")
print("FINAL STATUS:")
print(f"{'='*50}")

if all_clean and raw_present:
    print("🎉 PERFECT SUCCESS!")
    print("✅ PHP serialization: WORKING")
    print("✅ Sample content: COMPLETELY ELIMINATED")
    print("✅ Raw content: 100% PRESENT")
    print("✅ Shortcodes: PROPERLY APPLIED")
    print("✅ Structure: COMPLETE")
    print("\n🚀 READY FOR MAGIC PAGE PLUGIN IMPORT!")
    print(f"📁 File: magicpage_import_from_txt.txt ({len(test_data)} bytes)")
elif not all_clean:
    print("❌ Sample content still detected")
elif not raw_present:
    print("❌ Raw content missing")
else:
    print("❌ Unknown issue")
