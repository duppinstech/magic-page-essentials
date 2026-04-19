#!/usr/bin/env python3
"""
Test with minimal content to isolate the issue
"""

def create_minimal_test():
    # Read the working empty template
    with open("magicpage_template_clean.txt", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Test 1: Add just one character "X" to H1
    test1 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:1:"X";}}'
    )
    
    with open('magicpage_test_minimal.txt', 'w', encoding='utf-8') as f:
        f.write(test1)
    print("Created: magicpage_test_minimal.txt (H1 with just 'X')")
    
    # Test 2: Add just "test" to H1 (no HTML tags)
    test2 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:4:"test";}}'
    )
    
    with open('magicpage_test_simple.txt', 'w', encoding='utf-8') as f:
        f.write(test2)
    print("Created: magicpage_test_simple.txt (H1 with 'test')")
    
    # Test 3: Add HTML tags but short content
    test3 = template.replace(
        's:6:"pgn00b";a:1:{s:5:"label";s:11:"roadside-h1";}',
        's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";s:12:"<h1>Test</h1>";}}'
    )
    
    with open('magicpage_test_html.txt', 'w', encoding='utf-8') as f:
        f.write(test3)
    print("Created: magicpage_test_html.txt (H1 with '<h1>Test</h1>')")

if __name__ == "__main__":
    create_minimal_test()
