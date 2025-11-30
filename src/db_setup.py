"""Database setup module for Tesla casting data.

This module sets up an SQLite database with Tesla casting information.
It creates the 'castings' table and populates it from a CSV file.
"""

import sqlite3  # Standard library for SQLite database operations
import csv  # Standard library for reading CSV files


def setup_database():
    """Set up the SQLite database with Tesla casting data.

    Creates the 'castings' table if it doesn't exist and inserts data
    from 'tesla_castings.csv'. Uses 'INSERT OR IGNORE' to avoid duplicates.

    Table schema:
    - casting: Unique identifier for the casting (TEXT PRIMARY KEY)
    - years: Applicable years for this casting (TEXT)
    - cid: Casting Internal Description (TEXT)
    - low_power: Low power configuration (TEXT)
    - high_power: High power configuration (TEXT)
    - main_caps: Main material/caps (TEXT)
    - comments: Additional comments (TEXT, nullable)
    """
    # Connect to or create the database file
    conn = sqlite3.connect('castings.db')
    cursor = conn.cursor()

    # Create table with specified schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS castings (
            casting TEXT PRIMARY KEY,
            years TEXT NOT NULL,
            cid TEXT NOT NULL,
            low_power TEXT NOT NULL,
            high_power TEXT NOT NULL,
            main_caps TEXT NOT NULL,
            comments TEXT
        )
    ''')
    conn.commit()

    # Insert data from CSV file
    with open('data/tesla_castings.csv', 'r') as file:  # Open CSV with read mode
        reader = csv.DictReader(file)  # Use DictReader for header-based access
        for row in reader:  # Iterate through each row in the CSV
            try:
                # Insert row data into database, ignoring duplicates
                cursor.execute('''
                    INSERT OR IGNORE INTO castings (casting, years, cid, low_power, high_power, main_caps, comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Casting ID'],      # Unique casting identifier
                    row['Years'],           # Years column
                    row['CID'],             # Casting internal description
                    row['Low Power'],       # Low power config
                    row['High Power'],      # High power config
                    row['Main Caps'],       # Main material
                    row['Comments'] if 'Comments' in row else ''  # Optional comments
                ))
            except ValueError as e:  # Handle potential data type errors
                print(f"Error inserting row: {row}, {e}")
    conn.commit()  # Save all inserts to database
    conn.close()   # Close database connection
    print("Database setup complete.")


if __name__ == '__main__':
    setup_database()  # Run setup when script is executed directly
