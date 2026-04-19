#!/usr/bin/env python3
import re

print("SCRUBBING SAMPLE CONTENT WHILE PRESERVING FULL STRUCTURE")

with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Starting: {len(content)} chars, 38 paragraphs")

# Test baseline
import phpserialize
try:
    phpserialize.loads(content.encode('utf-8'))
    print("✅ Baseline passes PHP serialization")
except Exception as e:
    print(f"❌ Baseline broken: {e}")
    exit(1)

# Define ONLY the problematic sample content
sample_content = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County", 
    "Gazebos Towing"
]

# Scrub each piece of sample content VERY carefully
for sample in sample_content:
    if sample in content:
        print(f"🔥 Scrubbing: {sample}")
        
        # Find strings containing this sample and replace ONLY that string with a short generic replacement
        pattern = r's:(\d+):"([^"]*' + re.escape(sample) + r'[^"]*)"'
        
        def replacer(match):
            # Replace with a short generic message
            replacement_text = "Professional roadside assistance in [location], [meta_region_code]."
            replacement_length = len(replacement_text.encode('utf-8'))
            return f's:{replacement_length}:"{replacement_text}"'
        
        old_content = content
        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        
        # Test after each replacement
        try:
            phpserialize.loads(content.encode('utf-8'))
            print(f"   ✅ Still valid after scrubbing {sample}")
        except Exception as e:
            print(f"   ❌ Broken after scrubbing {sample}: {e}")
            print("   🔄 Reverting this change")
            content = old_content
            continue

print(f"After scrubbing: {len(content)} chars")

# Write the scrubbed version
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Final comprehensive test
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Scrubbed file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Re-analyze the scrubbed content
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    # Count content
    h1_count = final_content.count('<h1>')
    p_count = final_content.count('<p>')
    ul_count = final_content.count('<ul>')
    location_count = final_content.count('[location]')
    
    print(f"✅ Final structure: {h1_count} H1, {p_count} paragraphs, {ul_count} UL")
    print(f"✅ [location] shortcodes: {location_count}")
    
    # Final sample content check
    print("\nFinal sample content check:")
    all_clean = True
    for phrase in sample_content:
        if phrase in final_content:
            print(f"❌ STILL FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ SCRUBBED: {phrase}")
    
    # Check raw content is preserved
    raw_preserved = final_content.count('Jump Start') > 0
    print(f"✅ Raw content preserved: {raw_preserved}")
    
    if all_clean and raw_preserved:
        print("\n🎉 PERFECT! Full structure + raw content + NO sample contamination!")
        print("🚀 READY FOR MPP IMPORT!")
    elif all_clean:
        print("\n✅ Sample content eliminated but check raw content")
    else:
        print("\n❌ Some sample content still remains")
    
except Exception as e:
    print(f'\n❌ Final PHP error: {e}')
