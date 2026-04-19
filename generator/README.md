# Magic Page Plugin (MPP) content generator

This folder originally held the **Python** prototype that builds a PHP-serialized spintax file for Magic Page import.

## In-plugin generator (recommended)

The same logic now runs **inside WordPress Essentials** (`includes/class-magicpage-import-generator.php`):

1. Go to **Magic Page → Essentials** and ensure **Import generator** is enabled.
2. Open **Magic Page → Import generator**.
3. Paste raw HTML/text, upload a `.txt` file, or paste a **public** Google Doc link (must be “Anyone with the link can view”).
4. Download `magicpage_import_from_txt.txt` and import it into Magic Page.

No Python or local CLI is required for that workflow.

## Legacy Python files (optional)

- **`magicpage_from_txt.py`** — Original script; kept for reference or offline use.
- **`magicpage_raw.txt`** — Example source content.
- **`magicpage_import_from_txt.txt`** — Example output (when generated).

Requirements for the script: Python 3.x and `phpserialize` (`pip install phpserialize`).

## Content sections

- **Roadside**, **Heavy**, **Equipment**, **Towing** — each with versioned paragraphs and UL blocks per the template.
