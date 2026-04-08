import aiosqlite
import os
import csv
import io
from typing import List, Optional

# Store DB in the backend/data/ directory (created on startup)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inklayer.db')


async def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    UNIQUE NOT NULL,
                tag         TEXT    NOT NULL DEFAULT 'general',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()


async def add_subscriber(email: str, tag: str = "general") -> bool:
    """
    Insert a new subscriber.
    Returns True on success, False if email already exists (duplicate).
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                'INSERT INTO subscribers (email, tag) VALUES (?, ?)',
                (email, tag)
            )
            await db.commit()
            return True
    except aiosqlite.IntegrityError:
        return False


async def get_all_subscribers(tag: Optional[str] = None) -> List[dict]:
    """
    Fetch all subscribers, optionally filtered by tag.
    Returns a list of dicts ordered by most recent first.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if tag:
            query = 'SELECT * FROM subscribers WHERE tag = ? ORDER BY created_at DESC'
            async with db.execute(query, (tag,)) as cursor:
                rows = await cursor.fetchall()
        else:
            async with db.execute('SELECT * FROM subscribers ORDER BY created_at DESC') as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_subscriber_tag(email: str, tag: str) -> bool:
    """
    Update the tag of an existing subscriber.
    Returns True if a row was updated, False if email not found.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'UPDATE subscribers SET tag = ? WHERE email = ?',
            (tag, email)
        )
        await db.commit()
        return cursor.rowcount > 0


async def export_subscribers_csv(tag: Optional[str] = None) -> str:
    """
    Export all subscribers (or a tagged subset) as a CSV string.
    """
    rows = await get_all_subscribers(tag=tag)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "email", "tag", "created_at"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


async def get_subscriber_emails(tag: Optional[str] = None) -> List[str]:
    """
    Return just the email addresses — used for bulk drop sending.
    """
    rows = await get_all_subscribers(tag=tag)
    return [r["email"] for r in rows]
