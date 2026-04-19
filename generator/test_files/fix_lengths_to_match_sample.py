#!/usr/bin/env python3
"""
Copy the exact string lengths from the working sample, even if they're wrong
This will test if MPP requires the exact same broken lengths to import
"""

import re

def extract_length_patterns(content):
    """Extract all s:LENGTH:"content" patterns with their positions"""
    patterns = []
    for match in re.finditer(r's:(\d+):"([^"]*)"', content):
        patterns.append({
            'start': match.start(),
            'end': match.end(), 
            'declared_length': int(match.group(1)),
            'content': match.group(2),
            'actual_length': len(match.group(2).encode('utf-8')),
            'full_match': match.group(0)
        })
    return patterns

def main():
    # Load both files
    with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
        sample_content = f.read()
    
    with open('magicpage_import_from_txt.txt', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Extract patterns from both
    sample_patterns = extract_length_patterns(sample_content)
    current_patterns = extract_length_patterns(current_content)
    
    print(f"Sample patterns: {len(sample_patterns)}")
    print(f"Current patterns: {len(current_patterns)}")
    
    # Find the H1 pattern specifically
    sample_h1 = None
    current_h1 = None
    
    for pattern in sample_patterns:
        if '"7xj2jn"' in sample_content[max(0, pattern['start']-20):pattern['start']]:
            sample_h1 = pattern
            break
    
    for pattern in current_patterns:
        if '"7xj2jn"' in current_content[max(0, pattern['start']-20):pattern['start']]:
            current_h1 = pattern
            break
    
    if sample_h1 and current_h1:
        print(f"\n=== H1 COMPARISON ===")
        print(f"Sample H1 declared length: {sample_h1['declared_length']}")
        print(f"Sample H1 actual length: {sample_h1['actual_length']}")
        print(f"Sample H1 content: {sample_h1['content']}")
        print(f"")
        print(f"Current H1 declared length: {current_h1['declared_length']}")
        print(f"Current H1 actual length: {current_h1['actual_length']}")
        print(f"Current H1 content: {current_h1['content']}")
        
        # Create a version that uses the EXACT same wrong length as sample
        print(f"\n=== CREATING MATCHED-LENGTH VERSION ===")
        
        # Replace current H1 with sample's exact length declaration
        new_content = current_content.replace(
            f's:{current_h1["declared_length"]}:"{current_h1["content"]}"',
            f's:{sample_h1["declared_length"]}:"{current_h1["content"]}"'
        )
        
        with open('magicpage_import_matched_lengths.txt', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Created: magicpage_import_matched_lengths.txt")
        print(f"This uses sample's length ({sample_h1['declared_length']}) with current content")

if __name__ == "__main__":
    main()
