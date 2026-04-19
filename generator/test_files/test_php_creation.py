#!/usr/bin/env python3
import phpserialize

# Create a PHP array structure using the phpserialize library
# instead of building the string manually

# Create the structure that should match our template
test_data = {
    b'spintax-shortcodes': {
        b'c0g3b1f': {
            b'label': b'roadside-meta-title',
            b'options': {
                b'8q6ubd': b'Test Title'
            }
        }
    }
}

print("Creating PHP serialization from Python data structure...")

try:
    # Serialize the data
    serialized = phpserialize.dumps(test_data)
    print(f"✅ Serialization successful! ({len(serialized)} bytes)")
    print("Serialized data:", serialized.decode('utf-8'))
    
    # Test deserialization
    deserialized = phpserialize.loads(serialized)
    print("✅ Deserialization successful!")
    print("Result:", deserialized)
    
    # Compare with our manual structure
    manual_structure = 'a:1:{s:18:"spintax-shortcodes";a:1:{s:7:"c0g3b1f";a:2:{s:5:"label";s:19:"roadside-meta-title";s:7:"options";a:1:{s:6:"8q6ubd";s:10:"Test Title";}}}}'
    
    print(f"\nManual structure: {manual_structure}")
    print(f"Generated structure: {serialized.decode('utf-8')}")
    
    if serialized.decode('utf-8') == manual_structure:
        print("✅ Structures match!")
    else:
        print("❌ Structures differ")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
# Let's also test what happens with a simple array
print("\nTesting simple array...")
simple_data = {b'test': b'value'}
try:
    simple_serialized = phpserialize.dumps(simple_data)
    print(f"Simple serialized: {simple_serialized.decode('utf-8')}")
    
    simple_deserialized = phpserialize.loads(simple_serialized)
    print(f"Simple deserialized: {simple_deserialized}")
except Exception as e:
    print(f"Simple test error: {e}")
