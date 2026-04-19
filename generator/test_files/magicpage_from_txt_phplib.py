#!/usr/bin/env python3
import re
import phpserialize

print("USING PHPSERIALIZE LIBRARY - 100% RAW DATA")

# Read raw content
with open('magicpage_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

def apply_shortcodes(text):
    text = re.sub(r'\b(Ringgold|Calhoun|Chattanooga|Trenton)\b', '[location]', text)
    text = re.sub(r'\b(GA|TN)\b', '[meta_region_code]', text)
    text = text.replace("Bell's Towing & Recovery", "[xfield_company-name]")
    return text

print("Processing raw content...")

# Extract H1
h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, re.IGNORECASE)
h1_text = apply_shortcodes(h1_match.group(1).strip()) if h1_match else "24/7 Roadside Assistance [location], [meta_region_code]"
h1_content = f'<h1>{h1_text}</h1>'

# Extract paragraphs (filter out button text and short lines)
sections = re.split(r'<h[12][^>]*>.*?</h[12]>', raw_text, flags=re.IGNORECASE)
raw_paragraphs = []
for section in sections:
    section = section.strip()
    if section and not section.startswith('*'):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        for line in lines:
            # Filter out button text, links, short lines, and separator lines
            if (line and not line.startswith('*') and len(line) > 30 and 
                not line.lower().startswith('button:') and 
                not line.lower().startswith('link:') and
                not line.startswith('_') and
                not line.lower().startswith('tel:')):
                p_text = apply_shortcodes(line)
                raw_paragraphs.append(f'<p>{p_text}</p>')

# Extract ALL UL items (complete list)
all_ul_items = re.findall(r'^\* (.+)$', raw_text, re.MULTILINE)

# Create individual UL options (each item as separate option)
ul_options = []
for i, item in enumerate(all_ul_items):
    ul_li = f'<li>{apply_shortcodes(item.strip())}</li>'
    # Use single quotes to avoid escaping issues in PHP serialization
    ul_single = f"<ul class='whiterail-ul'>{ul_li}</ul>"
    ul_options.append(ul_single)

print(f"Raw content: H1, {len(raw_paragraphs)} paragraphs, {len(ul_options)} UL items")

def get_paragraph(index):
    if index < len(raw_paragraphs):
        return raw_paragraphs[index]
    elif raw_paragraphs:
        return raw_paragraphs[index % len(raw_paragraphs)]
    else:
        return f'<p>[xfield_company-name] provides professional service in [location], [meta_region_code].</p>'

# Build complete structure using Python dict, then serialize with phpserialize
print("Building complete structure using phpserialize...")

# Create the structure as a Python dictionary
structure = {
    b'spintax-shortcodes': {}
}

fields = structure[b'spintax-shortcodes']

# Helper function to add a field
def add_field(field_id, label, options_dict):
    fields[field_id.encode('utf-8')] = {
        b'label': label.encode('utf-8'),
        b'options': {k.encode('utf-8'): v.encode('utf-8') for k, v in options_dict.items()}
    }

# ROADSIDE SECTION
add_field("c0g3b1f", "roadside-meta-title", {
    "8q6ubd": "24/7 Emergency Roadside Assistance [location], [meta_region_code] | [xfield_company-name]"
})

add_field("ex59ys", "roadside-meta-desc", {
    "ttpvck": "[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call for fuel delivery, vehicle lockouts, battery jumps, & more."
})

add_field("pgn00b", "roadside-h1", {
    "7xj2jn": h1_content
})

add_field("g92x2", "roadside-h2-1", {
    "8mch6i": "<h2>Emergency Roadside Services in [location], [meta_region_code]</h2>"
})

add_field("nyfvy", "roadside-img-1", {
    "icqjo8": '<img src="[xfield_company-name]-roadside-assistance-[location]-[meta_region_code].jpg" alt="24/7 Roadside Assistance [location] [meta_region_code]" />',
    "zqtylq": '<img src="[xfield_company-name]-emergency-roadside-[location]-[meta_region_code].jpg" alt="Emergency Roadside Services [location] [meta_region_code]" />',
    "rznnlkg": '<img src="[xfield_company-name]-towing-service-[location]-[meta_region_code].jpg" alt="Professional Towing Service [location] [meta_region_code]" />',
    "hcn5ub": '<img src="[xfield_company-name]-roadside-help-[location]-[meta_region_code].jpg" alt="Roadside Help [location] [meta_region_code]" />'
})

add_field("a71va", "roadside-paragraph-1", {
    "rc9iod": get_paragraph(0),
    "armq2": get_paragraph(1),
    "x58wh": get_paragraph(2),
    "u3ql0n": get_paragraph(3)
})

add_field("wxkwza", "roadside-paragraph-2", {
    "vl1dc": get_paragraph(4),
    "zwqt7": get_paragraph(5),
    "pqtkyq": get_paragraph(6),
    "jitca": get_paragraph(7)
})

add_field("3wnz47", "roadside-h2-2", {
    "9zek4": "<h2>Get Quick Roadside Assistance Near Me in [location], [meta_region_code]</h2>"
})

add_field("wirda", "roadside-img-2", {
    "siiztr": " ",
    "iwruys": " ",
    "h495ns": " ",
    "3a1nii": " "
})

add_field("fldy3", "roadside-paragraph-3", {
    "cz8bsk": get_paragraph(8),
    "yzjhed": get_paragraph(9),
    "dblfsd": get_paragraph(10),
    "n01p7o": get_paragraph(11)
})

add_field("q5man", "roadside-paragraph-4", {
    "r9x286": get_paragraph(12),
    "g6m6l": get_paragraph(13),
    "9cyet8": get_paragraph(14),
    "o4p9w": get_paragraph(15)
})

# UL with MANY more options - use up to 20 per section
roadside_ul_options = {}
for i in range(min(20, len(ul_options))):
    key_options = ["9vxk2p", "rddpm7", "6f5bza", "q1gbzg", "7xj2jn", "rc9iod", "armq2", "x58wh", "u3ql0n", "2k8fgh", "cz8bsk", "yzjhed", "dblfsd", "n01p7o", "r9x286", "g6m6l", "9cyet8", "o4p9w", "0ltva", "cnsb2c"]
    key = key_options[i % len(key_options)]
    roadside_ul_options[key] = ul_options[i]

add_field("feebkl", "roadside-ul", roadside_ul_options)

# Continue with ALL fields for complete template
add_field("52i9lm", "roadside-btn", {
    "4lzqbp": "Call [xfield_company-name] for Roadside Assistance in [location], [meta_region_code] Now!",
    "wb7x8v": "Get Roadside Assistance in [location], [meta_region_code] Now!"
})

add_field("ypk9mb", "roadside-paragraph-5", {
    "0ltva": get_paragraph(16),
    "cnsb2c": get_paragraph(17),
    "w00bpu": get_paragraph(18),
    "actg0a": get_paragraph(19)
})

add_field("j3sasf", "roadside-paragraph-6", {
    "dbs1hl": get_paragraph(20),
    "1tffej": " ",
    "70vbk8": " ",
    "wpjh5s2": get_paragraph(21)
})

# HEAVY SECTION
add_field("1e9th", "heavy-meta-title", {
    "ocikhb": "24/7 Heavy Duty Towing in [location], [meta_region_code] | [xfield_company-name]"
})

add_field("j0eud5", "heavy-meta-desc", {
    "9teic7": "[xfield_company-name] provides 24/7 heavy duty towing in [location]. Call for heavy towing, heavy recovery, & heavy duty roadside assistance."
})

add_field("s2bozf", "heavy-h1", {
    "3gj4as": "<h1>24/7 Heavy Tow Truck in [location], [meta_region_code]</h1>"
})

add_field("m8niv", "heavy-h2-1", {
    "7mc6qu": "<h2>24/7 Heavy Tow Truck in [location], [meta_region_code]</h2>"
})

add_field("fv2bh5", "heavy-img-1", {
    "db7sl": " ",
    "561yep": " ",
    "9oe81q": " ",
    "xjsi7d": " "
})

add_field("2nxs9j", "heavy-paragraph-1", {
    "x6a6u": get_paragraph(22),
    "0l4o2": get_paragraph(23),
    "m9dc4": get_paragraph(24),
    "y49n57": get_paragraph(25)
})

add_field("7m7bb", "heavy-paragraph-2", {
    "nk6vo": get_paragraph(26),
    "o4fgb": get_paragraph(27),
    "odypac": get_paragraph(28),
    "uch4jf": get_paragraph(29)
})

add_field("m6bsc", "heavy-h2-2", {
    "m83upi": "<h2>[location], [meta_region_code] Heavy Duty Towing Services You Can Trust</h2>"
})

add_field("aifese", "heavy-img-2", {
    "sq4db": " ",
    "24nwxr": " ",
    "2bguwo": " ",
    "42hwv": " "
})

add_field("matbz", "heavy-paragraph-3", {
    "30etu0j": get_paragraph(30),
    "uhkrxs": get_paragraph(31),
    "a2hz5n": get_paragraph(32),
    "12beqh": get_paragraph(33)
})

add_field("dqke2", "heavy-paragraph-4", {
    "jn80er": get_paragraph(34),
    "5cufpn": get_paragraph(35),
    "bss3r": get_paragraph(36),
    "bt8hn6": get_paragraph(37)
})

add_field("ej5zk", "heavy-h2-3", {
    "21wavl": "<h2>Heavy Duty Towing Near Me in [location], [meta_region_code]</h2>"
})

# Heavy UL with many more options
heavy_ul_options = {}
start_idx = 20  # Start after roadside items
for i in range(min(25, len(ul_options) - start_idx)):
    key_options = ["rddpm7", "6f5bza", "q1gbzg", "7xj2jn", "rc9iod", "armq2", "x58wh", "u3ql0n", "2k8fgh", "cz8bsk", "yzjhed", "dblfsd", "n01p7o", "r9x286", "g6m6l", "9cyet8", "o4p9w", "0ltva", "cnsb2c", "w00bpu", "actg0a", "dbs1hl", "wpjh5s2", "x6a6u", "0l4o2"]
    key = key_options[i % len(key_options)]
    if start_idx + i < len(ul_options):
        heavy_ul_options[key] = ul_options[start_idx + i]

add_field("2runon", "heavy-ul", heavy_ul_options)

add_field("9gy7jf", "heavy-btn", {
    "fx1lq": "GET HEAVY DUTY TOWING IN [location], [meta_region_code] NOW",
    "tis9sj": "GET HEAVY DUTY TOWING NEAR ME IN [location], [meta_region_code] NOW"
})

add_field("wmh9y", "heavy-paragraph-5", {
    "eyn08k": get_paragraph(38),
    "tx9eio": get_paragraph(39),
    "ffe3cb": get_paragraph(40),
    "7mzgzu": get_paragraph(41)
})

add_field("et1rzl", "heavy-paragraph-6", {
    "lgvh2": get_paragraph(42),
    "o5011": " ",
    "oouf6v": " ",
    "t1qp7r": " "
})

# EQUIPMENT SECTION
add_field("xqmzb", "equipment-meta-title", {
    "tisq38": "24/7 Heavy Equipment Towing in [location], [meta_region_code] | [xfield_company-name]"
})

add_field("9eh081", "equipment-meta-desc", {
    "wrmeis": "[xfield_company-name] provides 24/7 heavy equipment towing and heavy machinery towing in [location]."
})

add_field("5dnz3", "equipment-h1", {
    "uj26t": "<h1>24/7 Heavy Equipment Towing in [location], [meta_region_code]</h1>"
})

add_field("p14vgo", "equipment-h2-1", {
    "vq96": "<h2>[location], [meta_region_code] Heavy Equipment & Machinery Towing Service</h2>"
})

add_field("bguzaa", "equipment-img-1", {
    "qgt4gn": " ",
    "6sk5sh": " "
})

add_field("msa63f", "equipment-paragraph-1", {
    "vo9f1": get_paragraph(43),
    "7sjrl": get_paragraph(44),
    "i2om2t": get_paragraph(45),
    "4adix": get_paragraph(46)
})

add_field("qh3mqq", "equipment-paragraph-2", {
    "pzb65a": get_paragraph(47),
    "fq17l": get_paragraph(48),
    "k3dbi": get_paragraph(49),
    "0fte3": get_paragraph(50)
})

add_field("0q16o", "equipment-h2-2", {
    "7vnrdm": "<h2>Heavy Equipment Hauling Near Me in [location], [meta_region_code]</h2>"
})

add_field("niil7", "equipment-img-2", {
    "l3zslj": " ",
    "73k7sd": " "
})

add_field("dmaz9b", "equipment-paragraph-3", {
    "krgp86": get_paragraph(51),
    "ghffwc": get_paragraph(52),
    "m8zmf7": get_paragraph(53),
    "a86h8j": get_paragraph(54)
})

add_field("ryze2", "equipment-paragraph-4", {
    "j389re": get_paragraph(55),
    "d9067": get_paragraph(56),
    "ojjjm": get_paragraph(57),
    "mnrvn": get_paragraph(58)
})

add_field("febl7d", "equipment-ul", {
    "6f5bza": ul_options[8] if len(ul_options) > 8 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "q1gbzg": ul_options[9] if len(ul_options) > 9 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "7xj2jn": ul_options[10] if len(ul_options) > 10 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "rc9iod": ul_options[11] if len(ul_options) > 11 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>"
})

add_field("5c6d9t", "equipment-btn", {
    "ox60g8": "GET [location], [meta_region_code] HEAVY EQUIPMENT TOWING NOW"
})

add_field("b4hwgn", "equipment-h2-3", {
    "3z6t4e": "<h2>Get Professional Heavy Equipment Towing in [location], [meta_region_code]</h2>",
    "yydta": "<h2>Heavy Equipment Hauling Near Me in [location], [meta_region_code]</h2>"
})

add_field("t87nie", "equipment-paragraph-5", {
    "b8tlni": get_paragraph(59),
    "b2fj7j": get_paragraph(60),
    "65j5nw": get_paragraph(61),
    "9b94u": get_paragraph(62)
})

add_field("14qiq", "equipment-paragraph-6", {
    "8i83tm": get_paragraph(63),
    "l8tccn": get_paragraph(64),
    "nel29c": get_paragraph(65),
    "tpd17": get_paragraph(66)
})

# TOWING SECTION
add_field("bbih6j", "towing-meta-title", {
    "mlvcx": "24/7 Towing Company in [location], [meta_region_code] | Tow Truck Near Me"
})

add_field("b8xipc", "towing-meta-desc", {
    "q5k557": "[xfield_company-name] provides 24/7 emergency towing services in [location]. Call for a quick tow truck near me by a trusted towing company."
})

add_field("8byy4", "towing-h1", {
    "1wm5sc": "<h1>24/7 Towing Services in [location], [meta_region_code]</h1>"
})

add_field("xvtkuw", "towing-h2-1", {
    "w2hfeu": "<h2>Reliable Towing Services in [location], [meta_region_code]</h2>"
})

add_field("e84yns", "towing-img-1", {
    "yndpz": " ",
    "9dcnvc": " ",
    "0o5bhj": " ",
    "4hmfo": " "
})

add_field("vxkind", "towing-paragraph-1", {
    "ewqkze": get_paragraph(67),
    "9nqx6t": get_paragraph(68),
    "0qnoz": get_paragraph(69),
    "z1mrc": get_paragraph(70)
})

add_field("06sn8r", "towing-paragraph-2", {
    "rfz8aa": get_paragraph(71),
    "yzuxfy": get_paragraph(72),
    "m1r9d": get_paragraph(73),
    "zbmam": get_paragraph(74)
})

add_field("dk4z9t", "towing-h2-2", {
    "g8cl8": "<h2>[location], [meta_region_code]'s #1 Towing Company</h2>"
})

add_field("3rilxj", "towing-img-2", {
    "nle75": " ",
    "sqaksd": " ",
    "6q8eek": " ",
    "nb42a1": " "
})

add_field("6x8ojn", "towing-paragraph-3", {
    "31v258": get_paragraph(75),
    "56cvdh": get_paragraph(76),
    "l47dco": get_paragraph(77),
    "kvpz4l": get_paragraph(78)
})

add_field("fn3cy", "towing-paragraph-4", {
    "wfqzqh": get_paragraph(79),
    "xc9e1": get_paragraph(80),
    "71o2ze": get_paragraph(81),
    "2bhosg": get_paragraph(82)
})

add_field("bz4il", "towing-h2-3", {
    "wq0gnm": "<h2>Quick Tow Truck Services Near Me in [location], [meta_region_code]</h2>"
})

add_field("i2j7cm", "towing-paragraph-5", {
    "0jrs7i": get_paragraph(83),
    "ioti3": get_paragraph(84),
    "1d9sck": get_paragraph(85),
    "ssl63": get_paragraph(86)
})

add_field("xmipar", "towing-paragraph-6", {
    "gmtus7": " ",
    "64a6uo": get_paragraph(87),
    "hyfh0f": get_paragraph(88),
    "nibtr": get_paragraph(89)
})

add_field("g5jbni", "towing-ul", {
    "q1gbzg": ul_options[12] if len(ul_options) > 12 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "7xj2jn": ul_options[13] if len(ul_options) > 13 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "rc9iod": ul_options[14] if len(ul_options) > 14 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>",
    "armq2": ul_options[15] if len(ul_options) > 15 else "<ul class='whiterail-ul'><li>Service in [location]</li></ul>"
})

add_field("bfwu4e", "towing-btn", {
    "gro1ue": "Call a tow truck in [location], [meta_region_code]",
    "0of8hm": "QUICK TOW TRUCK [location], [meta_region_code]!",
    "5yum8": "Get a tow truck near me in [location], [meta_region_code] NOW!",
    "0z0wc": "Get a Tow Truck now in [location], [meta_region_code]!"
})

add_field("ge1q2g", "towing-h2-4", {
    "lbt0s8": "<h2>Need a Tow Truck Near Me in [location]?</h2>"
})

add_field("v5q5va", "roadside-h2-3", {
    "67z0iw": "<h2>Your Local [location] Roadside Assistance Company</h2>"
})

print(f"Built complete structure with {len(fields)} fields")

# Serialize using phpserialize
try:
    serialized_data = phpserialize.dumps(structure)
    print(f"✅ Serialization successful! ({len(serialized_data)} bytes)")
    
    # Test deserialization
    deserialized = phpserialize.loads(serialized_data)
    print("✅ Deserialization successful!")
    
    # Write to file
    with open('magicpage_import_from_txt.txt', 'wb') as f:
        f.write(serialized_data)
    
    print("✅ File written successfully!")
    print("🚀 READY FOR MPP IMPORT!")
    
except Exception as e:
    print(f"❌ Error: {e}")
