import phpserialize, json

with open("magicpage_import_from_txt.txt", "rb") as f:
    raw = f.read()

# Clean up
raw = raw.lstrip(b"\xef\xbb\xbf").strip()  # BOM + spaces/newlines

print("Starts with:", raw[:30])  # sanity check

data = phpserialize.loads(raw, decode_strings=True)

with open("magicpage_review.json", "w", encoding="utf-8") as out:
    json.dump(data, out, indent=2, ensure_ascii=False)

print("✅ JSON review written")
