#!/usr/bin/env python3

# Read both files
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    sample = f.read()
    
with open('magicpage_import_from_txt_FINAL.txt', 'r', encoding='utf-8') as f:
    our_file = f.read()

# Split by semicolons and compare
sample_parts = sample.split(';')
our_parts = our_file.split(';')

print(f"Sample parts: {len(sample_parts)}")
print(f"Our file parts: {len(our_parts)}")

# Find the first difference
for i, (sample_part, our_part) in enumerate(zip(sample_parts, our_parts)):
    if sample_part != our_part:
        print(f"\nFirst difference at part {i}:")
        print(f"Sample: {repr(sample_part[-50:])}")
        print(f"Our file: {repr(our_part[-50:])}")
        
        # Show next few parts for context
        print(f"\nNext sample part: {repr(sample_parts[i+1][:50])}")
        print(f"Next our part: {repr(our_parts[i+1][:50])}")
        break

# If our file has more parts, show the extra ones
if len(our_parts) > len(sample_parts):
    print(f"\nExtra parts in our file:")
    for i in range(len(sample_parts), len(our_parts)):
        print(f"Part {i}: {repr(our_parts[i][:100])}")
        
# Check if there are any malformed patterns
import re
malformed = re.findall(r';;|;[^s}]', our_file)
if malformed:
    print(f"\nFound malformed patterns: {malformed[:5]}")
