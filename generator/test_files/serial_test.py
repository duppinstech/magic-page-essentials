import phpserialize
import sys

def validate_serialized_file(filename):
    with open(filename, "rb") as f:
        raw = f.read().strip()

    print(f"Loaded serialized data ({len(raw)} bytes)\n")

    try:
        # Try to unserialize
        data = phpserialize.loads(raw, decode_strings=True)
        print("✅ Successfully unserialized.")

        # Re-serialize
        reserialized = phpserialize.dumps(data).decode("utf-8")

        if raw.decode("utf-8") == reserialized:
            print("✅ Round-trip matches exactly.")
        else:
            print("⚠️ Round-trip differs. Possible count mismatch or whitespace issue.")
            with open("original.txt", "w", encoding="utf-8") as f1, \
                 open("reserialized.txt", "w", encoding="utf-8") as f2:
                f1.write(raw.decode("utf-8", errors="replace"))
                f2.write(reserialized)
            print("Saved original.txt and reserialized.txt for manual diff.")

    except Exception as e:
        print("❌ Error during unserialize:")
        print(str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_serialized.py <input_file>")
        sys.exit(1)

    validate_serialized_file(sys.argv[1])
