#!/usr/bin/env python3
import re

# Read both files
with open('magicpage_export_sample.txt', 'r', encoding='utf-8') as f:
    sample = f.read()
    
with open('magicpage_import_from_txt_FINAL.txt', 'r', encoding='utf-8') as f:
    our_file = f.read()

print("=== STRUCTURE COMPARISON ===")

# Compare basic structure
print(f"Sample file size: {len(sample)}")
print(f"Our file size: {len(our_file)}")

# Check opening structure
sample_start = sample[:200]
our_start = our_file[:200]

print(f"\nSample starts: {repr(sample_start)}")
print(f"Our file starts: {repr(our_start)}")
print(f"Opening match: {sample_start == our_start}")

# Check closing structure  
sample_end = sample[-100:]
our_end = our_file[-100:]

print(f"\nSample ends: {repr(sample_end)}")
print(f"Our file ends: {repr(our_end)}")
print(f"Closing match: {sample_end == our_end}")

# Check brace/semicolon counts
sample_open = sample.count('{')
sample_close = sample.count('}')
sample_semi = sample.count(';')

our_open = our_file.count('{')
our_close = our_file.count('}')
our_semi = our_file.count(';')

print(f"\nSample: {{ {sample_open}, }} {sample_close}, ; {sample_semi}")
print(f"Our file: {{ {our_open}, }} {our_close}, ; {our_semi}")

# Find potential structural differences
if sample_open != our_open or sample_close != our_close or sample_semi != our_semi:
    print("❌ STRUCTURAL MISMATCH FOUND!")
else:
    print("✅ Structure counts match")
