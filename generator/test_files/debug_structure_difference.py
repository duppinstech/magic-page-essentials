#!/usr/bin/env python3
"""
Debug the exact differences between working empty template and content version
"""

def analyze_structure_differences():
    # Read both files
    with open('magicpage_template_clean.txt', 'r', encoding='utf-8') as f:
        empty_template = f.read()
    
    with open('magicpage_import_simple.txt', 'r', encoding='utf-8') as f:
        content_version = f.read()
    
    print("=== STRUCTURE ANALYSIS ===")
    print(f"Empty template length: {len(empty_template)}")
    print(f"Content version length: {len(content_version)}")
    
    # Check if the basic structure is maintained
    if empty_template in content_version:
        print("✅ Empty template structure is contained in content version")
    else:
        print("❌ Empty template structure is NOT contained in content version")
    
    # Find the H1 field in both
    import re
    
    # Empty template H1
    empty_h1 = re.search(r's:6:"pgn00b";[^}]+}', empty_template)
    content_h1 = re.search(r's:6:"pgn00b";[^}]+}}', content_version)  # Note extra } for options
    
    print(f"\n=== H1 FIELD COMPARISON ===")
    if empty_h1:
        print(f"Empty H1:   {empty_h1.group(0)}")
    if content_h1:
        print(f"Content H1: {content_h1.group(0)[:100]}...")
    
    # Check paragraph-1
    empty_p1 = re.search(r's:5:"a71va";[^}]+}', empty_template)
    content_p1 = re.search(r's:5:"a71va";[^}]+}}', content_version)
    
    print(f"\n=== PARAGRAPH-1 FIELD COMPARISON ===")
    if empty_p1:
        print(f"Empty P1:   {empty_p1.group(0)}")
    if content_p1:
        print(f"Content P1: {content_p1.group(0)[:100]}...")
    
    # Check for any structural issues
    print(f"\n=== STRUCTURAL VALIDATION ===")
    
    # Count braces
    empty_open = empty_template.count('{')
    empty_close = empty_template.count('}')
    content_open = content_version.count('{')
    content_close = content_version.count('}')
    
    print(f"Empty - Open braces: {empty_open}, Close braces: {empty_close}, Balanced: {empty_open == empty_close}")
    print(f"Content - Open braces: {content_open}, Close braces: {content_close}, Balanced: {content_open == content_close}")
    
    # Check semicolons
    empty_semi = empty_template.count(';')
    content_semi = content_version.count(';')
    print(f"Empty semicolons: {empty_semi}")
    print(f"Content semicolons: {content_semi}")
    
    # Check if all field IDs are present in both
    field_ids = ['c0g3b1f', 'ex59ys', 'pgn00b', 'a71va']  # Sample of field IDs
    
    print(f"\n=== FIELD ID CHECK ===")
    for field_id in field_ids:
        in_empty = field_id in empty_template
        in_content = field_id in content_version
        print(f"{field_id}: Empty={in_empty}, Content={in_content}")

if __name__ == "__main__":
    analyze_structure_differences()
