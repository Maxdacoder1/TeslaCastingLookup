"""FastAPI application for Tesla casting lookup.

This module provides a REST API to look up Tesla casting information
by casting identifier. It serves data from an SQLite database.
"""

# Third-party imports for web framework and database operations
from fastapi import FastAPI, HTTPException, Query  # FastAPI framework and exception handling
import sqlite3  # SQLite database interface for data retrieval

# Initialize FastAPI application instance with metadata for API documentation
app = FastAPI(title="Tesla Casting API", description="API for querying Tesla casting data")


@app.get("/lookup/{casting}")
async def lookup_casting(casting: str):
    """Look up a Tesla casting by its identifier.

    Retrieves casting details from the database based on the provided
    casting ID. Returns 200 with data if found, 404 if not found,
    or 500 for database errors.

    Args:
        casting: Unique string identifier for the casting

    Returns:
        JSON object with casting details

    Raises:
        HTTPException: 404 if casting not found, 500 for database errors
    """
    # Attempt to query the database
    try:
        conn = sqlite3.connect('castings.db')  # Connect to database
        cursor = conn.cursor()                 # Create cursor for operations
        # Execute query to find casting by ID
        cursor.execute('SELECT casting, years, cid, low_power, high_power, main_caps, comments FROM castings WHERE casting = ?', (casting,))
        row = cursor.fetchone()  # Fetch single result row
    except sqlite3.Error as e:  # Handle database connection/operation errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()  # Always close connection, even if error occurs

    if row:  # If a row was found (casting exists)
        # Construct JSON response from row data
        data = {
            "casting": row[0],      # Casting identifier
            "years": row[1],        # Applicable years
            "cid": row[2],          # Casting internal description
            "low_power": row[3],    # Low power configuration
            "high_power": row[4],   # High power configuration
            "main_caps": row[5],    # Main material/caps
            "comments": row[6]      # Additional comments
        }
        return data
    else:  # No row found for this casting ID
        raise HTTPException(status_code=404, detail="Casting not found")


@app.get("/castings")
async def get_castings(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100)):
    """Get paginated list of all castings.

    Returns a list of all castings with basic info for browsing.
    Used by the web front-end to display paginated table of castings.

    Args:
        page: Page number (1-based, minimum 1)
        limit: Number of items per page (1-100 range enforced)

    Returns:
        JSON with castings list and pagination metadata
    """
    try:
        # Establish database connection for querying
        conn = sqlite3.connect('castings.db')
        cursor = conn.cursor()

        # Query total count of castings for pagination metadata
        cursor.execute('SELECT COUNT(*) FROM castings')
        total = cursor.fetchone()[0]

        # Calculate database offset based on page and limit
        offset = (page - 1) * limit

        # Fetch current page of castings (only basic fields for performance)
        cursor.execute('SELECT casting, years, cid FROM castings ORDER BY casting LIMIT ? OFFSET ?', (limit, offset))
        rows = cursor.fetchall()

        # Convert database rows to JSON-serializable dictionaries
        castings = [
            {
                "casting": row[0],
                "years": row[1],
                "cid": row[2]
            } for row in rows
        ]

        # Return paginated data with metadata for client-side pagination
        return {
            "castings": castings,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit  # Ceiling division
        }
    except sqlite3.Error as e:
        # Handle database operation failures
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # Ensure database connection is always closed
        conn.close()


@app.get("/search")
async def search_castings(q: str = Query(..., min_length=1)):
    """Search castings by query string across multiple fields.

    Performs fuzzy search using SQL LIKE operator on casting ID, CID, years,
    and comments fields. Returns complete matching records for detailed viewing.

    Args:
        q: Search query string (minimum 1 character enforced by parameter validation)

    Returns:
        JSON object containing search results, original query, and result count
    """
    try:
        # Establish database connection for search operation
        conn = sqlite3.connect('castings.db')
        cursor = conn.cursor()

        # Add wildcards to query for LIKE matching (fuzzy search)
        query = f"%{q}%"  # Surround with % for SQL LIKE consistency

        # Execute search query across all relevant text fields
        # Using multiple OR conditions for broader match coverage
        cursor.execute("""
            SELECT casting, years, cid, low_power, high_power, main_caps, comments
            FROM castings
            WHERE casting LIKE ? OR cid LIKE ? OR years LIKE ? OR comments LIKE ?
            ORDER BY casting
        """, (query, query, query, query))

        # Fetch all matching rows from database
        rows = cursor.fetchall()

        # Convert database rows to structured JSON response
        results = [
            {
                "casting": row[0],      # Unique casting identifier
                "years": row[1],        # Applicable model years
                "cid": row[2],          # Casting internal description
                "low_power": row[3],    # Low power configuration
                "high_power": row[4],   # High power configuration
                "main_caps": row[5],    # Main material specifications
                "comments": row[6]      # Additional casting notes
            } for row in rows
        ]

        # Return search results with metadata
        return {
            "results": results,        # Array of matching casting objects
            "query": q,               # Original search query for display
            "count": len(results)     # Number of matches found
        }
    except sqlite3.Error as e:
        # Handle database query failures
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # Ensure connection cleanup
        conn.close()
