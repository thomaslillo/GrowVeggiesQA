#!/usr/bin/env python3
"""
PDF to SQLite Converter

This script converts a PDF file into a SQLite database, storing each page as a row with:
- PDF page number
- Page image (either as a BLOB or reference to an external file)
- Section name
- Page text content
"""

import os
import sqlite3
import argparse
from pathlib import Path
import fitz  # PyMuPDF
import re
import io
from PIL import Image

def extract_section_name(text, current_section):
    """
    Extract section name from page text using heuristics.
    Returns the current section if no new section is detected.
    """
    # Look for patterns that might indicate section headers
    # This is a simple heuristic and might need adjustment based on the PDF structure
    section_patterns = [
        r'^(?:SECTION|Chapter|CHAPTER|PART)\s+\d+[.:]\s*(.*?)$',
        r'^(?:SECTION|Chapter|CHAPTER|PART)\s+(.*?)$',
        r'^(\d+\.\s+[A-Z][A-Za-z\s]+)$'
    ]
    
    lines = text.split('\n')
    for line in lines[:10]:  # Check first few lines for section headers
        line = line.strip()
        if not line:
            continue
            
        for pattern in section_patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                return match.group(1).strip()
    
    return current_section

def create_database(db_path):
    """Create the SQLite database and table structure."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table for PDF pages
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pdf_pages (
        id INTEGER PRIMARY KEY,
        page_number INTEGER NOT NULL,
        page_image BLOB,
        image_path TEXT,
        section_name TEXT,
        page_text TEXT
    )
    ''')
    
    conn.commit()
    return conn

def process_pdf(pdf_path, db_conn, images_folder=None, store_blob=True):
    """
    Process the PDF and store each page in the database.
    
    Args:
        pdf_path: Path to the PDF file
        db_conn: SQLite database connection
        images_folder: Folder to store page images (if not storing as BLOBs)
        store_blob: Whether to store images as BLOBs in the database
    """
    cursor = db_conn.cursor()
    
    # Create images folder if needed
    if not store_blob and images_folder:
        os.makedirs(images_folder, exist_ok=True)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    current_section = "Introduction"  # Default section name
    
    # Process each page
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Extract text
        text = page.get_text()
        
        # Try to detect section from text
        current_section = extract_section_name(text, current_section)
        
        # Handle page image
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
        img_data = pix.tobytes("jpeg")
        
        image_path = None
        image_blob = None
        
        if store_blob:
            # Store image directly in database
            image_blob = img_data
        else:
            # Save image to file and store path
            if images_folder:
                image_path = os.path.join(images_folder, f"page_{page_num + 1}.jpg")
                with open(image_path, 'wb') as img_file:
                    img_file.write(img_data)
        
        # Insert page data into database
        cursor.execute('''
        INSERT INTO pdf_pages (page_number, page_image, image_path, section_name, page_text)
        VALUES (?, ?, ?, ?, ?)
        ''', (page_num + 1, image_blob, image_path, current_section, text))
        
        # Print progress
        print(f"Processed page {page_num + 1}/{len(pdf_document)}, Section: {current_section}")
    
    # Commit changes
    db_conn.commit()
    pdf_document.close()

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to SQLite database')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--db_path', help='Path for the output SQLite database', 
                        default=None)
    parser.add_argument('--images_folder', help='Folder to store page images', 
                        default='page_images')
    parser.add_argument('--store_as_blob', action='store_true', 
                        help='Store images as BLOBs in the database')
    
    args = parser.parse_args()
    
    # Set default database path if not provided
    if args.db_path is None:
        pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        args.db_path = f"{pdf_name}.db"
    
    # Create database
    conn = create_database(args.db_path)
    
    try:
        # Process PDF
        process_pdf(
            args.pdf_path, 
            conn, 
            images_folder=args.images_folder if not args.store_as_blob else None,
            store_blob=args.store_as_blob
        )
        print(f"PDF successfully converted to SQLite database: {args.db_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
