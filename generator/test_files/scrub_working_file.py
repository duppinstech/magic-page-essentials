#!/usr/bin/env python3
import re

print("SCRUBBING sample content from working PHP file...")

# Read the working file
with open('magicpage_import_from_txt_CLEAN.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original size: {len(content)} chars")

# Define all sample content to eliminate
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
    "Raleigh Boulevard"
]

# Replace any string containing sample content with single space
for sample in sample_content:
    if sample in content:
        print(f"🔥 Found and scrubbing: {sample}")
        # Find strings containing this sample and replace with blank
        pattern = r's:\d+:"[^"]*' + re.escape(sample) + r'[^"]*"'
        content = re.sub(pattern, 's:1:" "', content, flags=re.DOTALL)

# Also replace any long paragraphs that might contain sample content
# Replace any paragraph longer than 200 chars with blank (except our UL)
def replacer(match):
    length = int(match.group(1))
    string_content = match.group(2)
    # Keep UL content and short content
    if '<ul class="whiterail-ul">' in string_content or length < 200:
        return match.group(0)  # Keep as is
    else:
        return 's:1:" "'  # Replace with blank

content = re.sub(r's:(\d+):"([^"]*)"', replacer, content, flags=re.DOTALL)

print(f"Scrubbed size: {len(content)} chars")

# Write the scrubbed file
with open('magicpage_import_from_txt.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Created: magicpage_import_from_txt.txt (SCRUBBED)")

# Test PHP serialization
import phpserialize
try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        test_data = f.read()
    phpserialize.loads(test_data)
    print('🎉 SUCCESS! PHP serialization still works!')
except Exception as e:
    print(f'❌ PHP error: {e}')

# Final verification
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
else:
    print("\n❌ Some sample content remains")
