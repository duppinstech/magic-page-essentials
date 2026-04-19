#!/usr/bin/env python3
"""Create minimal working raw-only file"""

def main():
    # Build minimal but correct PHP structure
    def php_string(content):
        length = len(content.encode('utf-8'))
        return f's:{length}:"{content}"'
    
    # Start with correct structure
    output = 'a:1:{s:18:"spintax-shortcodes";a:4:{'
    
    # Field 1: Meta title (with content)
    output += 's:7:"c0g3b1f";a:2:{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{s:6:"8q6ubd";'
    output += php_string('24/7 Emergency Roadside Assistance [location], [meta_region_code]')
    output += ';}}'
    
    # Field 2: H1 (with content)
    output += 's:6:"pgn00b";a:2:{s:5:"label";s:11:"roadside-h1";s:7:"options";a:1:{s:6:"7xj2jn";'
    output += php_string('<h1>24/7 Roadside Assistance [location], [meta_region_code]</h1>')
    output += ';}}'
    
    # Field 3: Paragraph (with content)
    output += 's:5:"a71va";a:2:{s:5:"label";s:20:"roadside-paragraph-1";s:7:"options";a:1:{s:6:"rc9iod";'
    output += php_string('Bell\'s Towing provides fast roadside assistance in [location], [meta_region_code]. Call us for emergency towing services.')
    output += ';}}'
    
    # Field 4: UL (with content)
    output += 's:6:"feebkl";a:2:{s:5:"label";s:11:"roadside-ul";s:7:"options";a:1:{s:6:"9vxk2p";'
    output += php_string('<ul class="whiterail-ul"><li>Jump Start [location], [meta_region_code]</li><li>Towing [location], [meta_region_code]</li></ul>')
    output += ';}}'
    
    # Close structure
    output += '}}'
    
    # Write file
    with open('test_raw_minimal.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Created test_raw_minimal.txt ({len(output)} bytes)")
    print("Testing PHP serialization...")

if __name__ == "__main__":
    main()
