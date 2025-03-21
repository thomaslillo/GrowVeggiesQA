#!/usr/bin/env python3
"""
Add Full-Text Search capabilities to the PDF SQLite database.

This script adds FTS5 virtual tables to enable efficient text searching
in the HomesteadTO Grow Veggies Textbook database.
"""

import sqlite3
import argparse
import os

def add_fts_to_database(db_path):
    """
    Add FTS5 virtual table to the database and populate it with text content.
    
    Args:
        db_path: Path to the SQLite database
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if FTS5 is available
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"SQLite version: {version}")
        
        # Test if FTS5 is available
        try:
            cursor.execute("CREATE VIRTUAL TABLE temp.fts_test USING fts5(content)")
            cursor.execute("DROP TABLE temp.fts_test")
            print("FTS5 is available.")
        except sqlite3.Error as e:
            print(f"FTS5 is not available: {e}")
            print("Trying FTS4 instead...")
            try:
                cursor.execute("CREATE VIRTUAL TABLE temp.fts_test USING fts4(content)")
                cursor.execute("DROP TABLE temp.fts_test")
                print("FTS4 is available.")
                fts_version = "fts4"
            except sqlite3.Error as e2:
                print(f"FTS4 is also not available: {e2}")
                print("Falling back to FTS3...")
                cursor.execute("CREATE VIRTUAL TABLE temp.fts_test USING fts3(content)")
                cursor.execute("DROP TABLE temp.fts_test")
                print("FTS3 is available.")
                fts_version = "fts3"
        else:
            fts_version = "fts5"
        
        # Create FTS virtual table for page text
        print(f"Creating FTS virtual table using {fts_version}...")
        
        if fts_version == "fts5":
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pdf_pages_fts USING fts5(
                page_number, 
                section_name, 
                page_text,
                content='pdf_pages',
                content_rowid='id'
            )
            """)
        else:
            # FTS3/FTS4 syntax
            cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS pdf_pages_fts USING {fts_version}(
                page_number, 
                section_name, 
                page_text,
                content=pdf_pages
            )
            """)
        
        # Populate the FTS table with data from the original table
        print("Populating FTS table with text data...")
        cursor.execute("""
        INSERT INTO pdf_pages_fts(rowid, page_number, section_name, page_text)
        SELECT id, page_number, section_name, page_text FROM pdf_pages
        """)
        
        # Create a trigger to keep the FTS table in sync with the main table for future updates
        print("Creating triggers to keep FTS table in sync...")
        
        # Trigger for inserts
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS pdf_pages_ai AFTER INSERT ON pdf_pages BEGIN
            INSERT INTO pdf_pages_fts(rowid, page_number, section_name, page_text)
            VALUES (new.id, new.page_number, new.section_name, new.page_text);
        END;
        """)
        
        # Trigger for updates
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS pdf_pages_au AFTER UPDATE ON pdf_pages BEGIN
            UPDATE pdf_pages_fts SET
                page_number = new.page_number,
                section_name = new.section_name,
                page_text = new.page_text
            WHERE rowid = old.id;
        END;
        """)
        
        # Trigger for deletes
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS pdf_pages_ad AFTER DELETE ON pdf_pages BEGIN
            DELETE FROM pdf_pages_fts WHERE rowid = old.id;
        END;
        """)
        
        conn.commit()
        print("FTS setup completed successfully!")
        
        # Test the FTS functionality
        print("\nTesting FTS functionality with a sample query...")
        cursor.execute("""
        SELECT page_number, section_name, snippet(pdf_pages_fts, 2, '<b>', '</b>', '...', 20)
        FROM pdf_pages_fts
        WHERE pdf_pages_fts MATCH 'grow'
        LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"Found {len(results)} matches (showing first 5):")
            for page_num, section, snippet in results:
                print(f"Page {page_num} ({section}): {snippet}")
        else:
            print("No matches found for the test query.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
        
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Add Full-Text Search to PDF SQLite database')
    parser.add_argument('db_path', help='Path to the SQLite database file', 
                        default="HomesteadTO Grow Veggies Textbook_2025 Edition.db", nargs='?')
    
    args = parser.parse_args()
    
    success = add_fts_to_database(args.db_path)
    
    if success:
        print("\nFull-Text Search has been successfully added to the database.")
        print("You can now perform efficient text searches using FTS syntax.")
    else:
        print("\nFailed to add Full-Text Search to the database.")

if __name__ == "__main__":
    main()
