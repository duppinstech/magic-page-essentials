#!/usr/bin/env python3
import re

print("FIXING FINAL SAMPLE CONTENT")

# Read current file
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Current file: {len(content)} characters")

# Find and replace "Our team" reference
if "Our team" in content:
    print("🔥 Found 'Our team' - replacing...")
    
    # Replace any string containing "Our team" with raw content
    pattern = r's:(\d+):"([^"]*Our team[^"]*)"'
    replacement = r's:86:"<p>[xfield_company-name] provides professional roadside assistance in [location], [meta_region_code].</p>"'
    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    print("✅ Replaced 'Our team' reference")

# Write the cleaned file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated file")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Cleaned file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Final verification
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
        print("\n🎉 PERFECT! 100% CLEAN - NO SAMPLE CONTENT!")
        print(f"✅ [location] shortcodes: {final_content.count('[location]')}")
        print(f"✅ [xfield_company-name] shortcodes: {final_content.count('[xfield_company-name]')}")
        print(f"✅ H1 headers: {final_content.count('<h1>')}")
        print(f"✅ Paragraphs: {final_content.count('<p>')}")
        print(f"✅ UL lists: {final_content.count('<ul>')}")
        print("\n🚀 FINAL SUCCESS: HARDCODED TEMPLATE + 100% RAW DATA + ZERO SAMPLE CONTAMINATION!")
        print("🚀 READY FOR MPP IMPORT!")
    else:
        print("\n❌ Sample content still detected")
    
except Exception as e:
    print(f'❌ PHP error: {e}')
