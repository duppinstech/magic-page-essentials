#!/usr/bin/env python3
import phpserialize

try:
    with open('magicpage_import_from_txt.txt', 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Test PHP deserialization
    result = phpserialize.loads(data)
    print("✅ PHP deserialization successful!")
    
    # Test round-trip
    serialized_back = phpserialize.dumps(result)
    if serialized_back == data:
        print("✅ Round-trip serialization matches!")
    else:
        print("❌ Round-trip serialization differs")
    
except Exception as e:
    print(f"❌ PHP serialization error: {e}")
