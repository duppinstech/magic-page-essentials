#!/usr/bin/env python3
"""
Create progressive tests to find what breaks the import
"""

def create_progressive_tests():
    # Read the working empty template
    with open("magicpage_template_clean.txt", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Test 2: Simple text without HTML
    test2 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:21:"Roadside Assistance";}}'
    )
    
    with open('magicpage_test2_text.txt', 'w', encoding='utf-8') as f:
        f.write(test2)
    print("Created: magicpage_test2_text.txt (simple text)")
    
    # Test 3: HTML tags but short
    test3 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:26:"<h1>Roadside Assistance</h1>";}}'
    )
    
    with open('magicpage_test3_html.txt', 'w', encoding='utf-8') as f:
        f.write(test3)
    print("Created: magicpage_test3_html.txt (short HTML)")
    
    # Test 4: Longer text without special characters
    test4 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:50:"<h1>24/7 Roadside Assistance Ringgold Georgia</h1>";}}'
    )
    
    with open('magicpage_test4_longer.txt', 'w', encoding='utf-8') as f:
        f.write(test4)
    print("Created: magicpage_test4_longer.txt (longer text, no special chars)")
    
    # Test 5: With comma (original has comma)
    test5 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:46:"<h1>24/7 Roadside Assistance Ringgold, GA</h1>";}}'
    )
    
    with open('magicpage_test5_comma.txt', 'w', encoding='utf-8') as f:
        f.write(test5)
    print("Created: magicpage_test5_comma.txt (exact H1 content)")
    
    # Test 6: Add paragraph content too (the issue might be multiple fields)
    test6 = test5.replace(
        's:5:"a71va";a:1:{s:5:"label";s:20:"roadside-paragraph-1";}',
        's:5:"a71va";a:2:{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{s:6:"rc9iod";s:20:"Short paragraph text";}}'
    )
    
    with open('magicpage_test6_two_fields.txt', 'w', encoding='utf-8') as f:
        f.write(test6)
    print("Created: magicpage_test6_two_fields.txt (H1 + short paragraph)")

if __name__ == "__main__":
    create_progressive_tests()
