"""FastAPI application for Tesla casting lookup.

This module provides a REST API to look up Tesla casting information
by casting identifier. It serves data from an SQLite database.
"""

from fastapi import FastAPI, HTTPException, Query  # FastAPI framework and exception handling
import sqlite3  # SQLite database interface


# Initialize FastAPI application instance
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

    Args:
        page: Page number (1-based)
        limit: Number of items per page

    Returns:
        JSON with castings list and pagination info
    """
    try:
        conn = sqlite3.connect('castings.db')
        cursor = conn.cursor()

        # Get total count
        cursor.execute('SELECT COUNT(*) FROM castings')
        total = cursor.fetchone()[0]

        # Calculate offset
        offset = (page - 1) * limit

        # Get paginated results
        cursor.execute('SELECT casting, years, cid FROM castings ORDER BY casting LIMIT ? OFFSET ?', (limit, offset))
        rows = cursor.fetchall()

        castings = [
            {
                "casting": row[0],
                "years": row[1],
                "cid": row[2]
            } for row in rows
        ]

        return {
            "castings": castings,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()


@app.get("/search")
async def search_castings(q: str = Query(..., min_length=1)):
    """Search castings by query string.

    Searches across casting ID, CID, and comments fields.

    Args:
        q: Search query

    Returns:
        JSON with matching castings
    """
    try:
        conn = sqlite3.connect('castings.db')
        cursor = conn.cursor()

        query = f"%{q}%"
        cursor.execute("""
            SELECT casting, years, cid, low_power, high_power, main_caps, comments
            FROM castings
            WHERE casting LIKE ? OR cid LIKE ? OR years LIKE ? OR comments LIKE ?
            ORDER BY casting
        """, (query, query, query, query))

        rows = cursor.fetchall()
        results = [
            {
                "casting": row[0],
                "years": row[1],
                "cid": row[2],
                "low_power": row[3],
                "high_power": row[4],
                "main_caps": row[5],
                "comments": row[6]
            } for row in rows
        ]

        return {"results": results, "query": q, "count": len(results)}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()
