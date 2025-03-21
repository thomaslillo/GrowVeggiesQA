# PDF to SQLite Converter

This tool converts the "HomesteadTO Grow Veggies Textbook_2025 Edition.pdf" into a SQLite database, storing each page with its metadata for easy querying and retrieval.

## Database Structure

The SQLite database contains a single table called `pdf_pages` with the following columns:

- `id`: Primary key (auto-incremented)
- `page_number`: PDF page number
- `page_image`: JPEG image of the page stored as a BLOB (when using `--store_as_blob` option)
- `image_path`: Reference to an external image file (when not using `--store_as_blob` option)
- `section_name`: Section name that the page belongs to
- `page_text`: Full text content of the page as a string

Additionally, the database includes a virtual table `pdf_pages_fts` that enables full-text search capabilities.

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- Virtual environment (recommended)

### Installation Steps

1. Clone this repository or download the files to your local machine.

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Converter

The script can be run in two modes:

#### Option 1: Store Images as BLOBs in the Database

This option stores the page images directly in the database as binary objects:

```bash
python pdf_to_sqlite.py "HomesteadTO Grow Veggies Textbook_2025 Edition.pdf" --store_as_blob
```

#### Option 2: Store Images as External Files

This option saves the page images to an external folder and stores the file paths in the database:

```bash
python pdf_to_sqlite.py "HomesteadTO Grow Veggies Textbook_2025 Edition.pdf" --images_folder "page_images"
```

### Enabling Full-Text Search

After creating the database, you can enable full-text search capabilities by running:

```bash
python add_fts_to_db.py
```

This script:
1. Creates a virtual FTS5 table (falls back to FTS4 or FTS3 if necessary)
2. Populates it with text data from the original table
3. Sets up triggers to keep the FTS table in sync with the main table

### Additional Options

You can specify a custom output database path:

```bash
python pdf_to_sqlite.py "HomesteadTO Grow Veggies Textbook_2025 Edition.pdf" --db_path "custom_name.db"
```

## Usage Examples

### Querying the Database

You can use standard SQLite queries to retrieve information from the database:

```python
import sqlite3
import io
from PIL import Image

# Connect to the database
conn = sqlite3.connect('HomesteadTO Grow Veggies Textbook_2025 Edition.db')
cursor = conn.cursor()

# Example 1: Get all pages from a specific section
cursor.execute("SELECT page_number, page_text FROM pdf_pages WHERE section_name = '1. Growth stage'")
for page_num, text in cursor.fetchall():
    print(f"Page {page_num}: {text[:100]}...")  # Print first 100 chars of each page

# Example 2: Search for specific content
cursor.execute("SELECT page_number, section_name FROM pdf_pages WHERE page_text LIKE '%tomato%'")
for page_num, section in cursor.fetchall():
    print(f"Found 'tomato' on page {page_num} in section '{section}'")

# Example 3: Extract and display an image (if stored as BLOB)
cursor.execute("SELECT page_image FROM pdf_pages WHERE page_number = 1")
img_data = cursor.fetchone()[0]
if img_data:
    img = Image.open(io.BytesIO(img_data))
    img.show()  # Display the image

# Close the connection
conn.close()
```

### Using Full-Text Search

Full-text search provides more powerful and efficient text searching capabilities:

```python
import sqlite3

# Connect to the database
conn = sqlite3.connect('HomesteadTO Grow Veggies Textbook_2025 Edition.db')
cursor = conn.cursor()

# Example 1: Basic FTS query
cursor.execute("""
SELECT page_number, section_name 
FROM pdf_pages_fts 
WHERE pdf_pages_fts MATCH 'tomato'
ORDER BY page_number
""")
for page_num, section in cursor.fetchall():
    print(f"Found 'tomato' on page {page_num} in section '{section}'")

# Example 2: Using the snippet function to show context
cursor.execute("""
SELECT page_number, snippet(pdf_pages_fts, 2, '<b>', '</b>', '...', 20) 
FROM pdf_pages_fts 
WHERE pdf_pages_fts MATCH 'planting AND seeds'
LIMIT 5
""")
for page_num, snippet in cursor.fetchall():
    print(f"Page {page_num}: {snippet}")

# Example 3: Advanced query with phrase search
cursor.execute("""
SELECT page_number, section_name 
FROM pdf_pages_fts 
WHERE pdf_pages_fts MATCH '"organic fertilizer"'
""")
for page_num, section in cursor.fetchall():
    print(f"Found phrase 'organic fertilizer' on page {page_num} in section '{section}'")

# Close the connection
conn.close()
```

## Database Statistics

- Total pages in database: 219
- Sections in the document:
  - Introduction
  - 1. Growth stage
  - 4. Seedlings grow

## Troubleshooting

If you encounter any issues:

1. Make sure the PDF file exists in the specified path
2. Verify that all dependencies are installed correctly
3. Check that you have sufficient disk space for the database (especially when storing images as BLOBs)

## License

This project is available for internal use only.

## Last Updated

March 21, 2025
