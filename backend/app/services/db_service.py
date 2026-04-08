import aiosqlite
import os

# Store DB in the root backend directory
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data.db')

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def add_subscriber(email: str) -> bool:
    """Returns True if successful, False if email already exists."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
            await db.commit()
            return True
    except aiosqlite.IntegrityError:
        return False

async def get_all_subscribers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM subscribers ORDER BY created_at DESC') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
