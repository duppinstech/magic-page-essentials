#!/usr/bin/env python3
import re

print("FINAL SCRUB: Remove ALL sample content from working version")

# Read the working version
with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Starting with working version ({len(content)} chars)")

# Test it first
import phpserialize
try:
    phpserialize.loads(content.encode('utf-8'))
    print("✅ Starting version passes PHP serialization")
except Exception as e:
    print(f"❌ Starting version broken: {e}")
    exit(1)

# Define ALL sample content to eliminate
sample_content = [
    "Our team of top-notch operators",
    "Coastal Towing", 
    "Wilson County",
    "Gazebos Towing",
    "Rocky Mount",
    "I-95",
    "Route 301", 
    "Route 42",
    "U.S. 64",
    "Peachtree Street",
    "Raleigh Boulevard",
    "Edgecombe County",
    "Nash County",
    "Halifax County",
    "Franklin County",
    "Johnston County"
]

# Scrub each piece of sample content
for sample in sample_content:
    if sample in content:
        print(f"🔥 Scrubbing: {sample}")
        
        # Find and replace any string containing this sample with a blank
        pattern = r's:(\d+):"([^"]*' + re.escape(sample) + r'[^"]*)"'
        
        def replacer(match):
            # Replace with single space
            return 's:1:" "'
        
        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        
        # Test after each scrub
        try:
            phpserialize.loads(content.encode('utf-8'))
            print(f"   ✅ Still valid after scrubbing {sample}")
        except Exception as e:
            print(f"   ❌ Broken after scrubbing {sample}: {e}")
            break

print(f"After scrubbing: {len(content)} chars")

# Write the scrubbed version
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Final test
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print(f'🎉 SUCCESS! Scrubbed file passes PHP serialization! ({len(test_data)} bytes)')
    
    # Verify no sample content remains
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    print("\nFinal verification:")
    all_clean = True
    for phrase in sample_content:
        if phrase in final_content:
            print(f"❌ STILL FOUND: {phrase}")
            all_clean = False
        else:
            print(f"✅ SCRUBBED: {phrase}")
    
    if all_clean:
        print("\n🎉 ALL SAMPLE CONTENT ELIMINATED!")
        print(f"✅ Contains [location]: {'[location]' in final_content}")
        print(f"✅ Contains [meta_region_code]: {'[meta_region_code]' in final_content}")
        
        # Count content
        h1_count = final_content.count('<h1>')
        p_count = final_content.count('<p>')
        ul_count = final_content.count('<ul>')
        print(f"✅ Content: {h1_count} H1, {p_count} paragraphs, {ul_count} UL sections")
        print("\n🎉 READY FOR MPP IMPORT!")
    else:
        print("\n❌ Some sample content still remains")
    
except Exception as e:
    print(f'\n❌ Final PHP error: {e}')
