"""
Custom database module for Ableton Buddy thread management.
Provides SQLite-based thread tracking separate from Marvin's internal storage.
"""

import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os


@dataclass
class AbletonThread:
    """Model for tracking Ableton Buddy threads."""

    thread_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    first_message_preview: Optional[str] = None
    title: Optional[str] = None


async def get_db_path() -> str:
    """Get the database path for the custom thread table."""
    # Use the same database as Marvin
    return "./ableton_buddy.db"


async def init_custom_db():
    """Initialize the custom ableton_threads table."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ableton_threads (
                thread_id TEXT PRIMARY KEY,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                message_count INTEGER DEFAULT 0,
                first_message_preview TEXT,
                title TEXT
            )
        """)
        await db.commit()


async def register_thread(thread_id: str, first_message: Optional[str] = None) -> None:
    """Register a new thread in the tracking table."""
    db_path = await get_db_path()
    now = datetime.now()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO ableton_threads 
            (thread_id, created_at, updated_at, message_count, first_message_preview)
            VALUES (?, ?, ?, ?, ?)
        """,
            (thread_id, now, now, 0, first_message),
        )
        await db.commit()


async def get_tracked_threads() -> List[AbletonThread]:
    """Get all tracked threads ordered by updated_at DESC."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        async with db.execute("""
            SELECT thread_id, created_at, updated_at, message_count, 
                   first_message_preview, title
            FROM ableton_threads 
            ORDER BY updated_at DESC
        """) as cursor:
            rows = await cursor.fetchall()

            threads = []
            for row in rows:
                threads.append(
                    AbletonThread(
                        thread_id=row[0],
                        created_at=datetime.fromisoformat(row[1]),
                        updated_at=datetime.fromisoformat(row[2]),
                        message_count=row[3],
                        first_message_preview=row[4],
                        title=row[5],
                    )
                )
            return threads


async def get_tracked_thread(thread_id: str) -> Optional[AbletonThread]:
    """Get a specific tracked thread by ID."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            """
            SELECT thread_id, created_at, updated_at, message_count, 
                   first_message_preview, title
            FROM ableton_threads 
            WHERE thread_id = ?
        """,
            (thread_id,),
        ) as cursor:
            row = await cursor.fetchone()

            if row:
                return AbletonThread(
                    thread_id=row[0],
                    created_at=datetime.fromisoformat(row[1]),
                    updated_at=datetime.fromisoformat(row[2]),
                    message_count=row[3],
                    first_message_preview=row[4],
                    title=row[5],
                )
            return None


async def update_thread_metadata(
    thread_id: str,
    message_count: Optional[int] = None,
    last_message: Optional[str] = None,
    title: Optional[str] = None,
) -> None:
    """Update thread metadata."""
    db_path = await get_db_path()
    now = datetime.now()

    # Build dynamic update query
    updates = ["updated_at = ?"]
    params = [now]

    if message_count is not None:
        updates.append("message_count = ?")
        params.append(message_count)

    if last_message is not None:
        updates.append("first_message_preview = ?")
        params.append(last_message)

    if title is not None:
        updates.append("title = ?")
        params.append(title)

    params.append(thread_id)

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            f"""
            UPDATE ableton_threads 
            SET {", ".join(updates)}
            WHERE thread_id = ?
        """,
            params,
        )
        await db.commit()


async def delete_tracked_thread(thread_id: str) -> None:
    """Remove a thread from tracking."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            DELETE FROM ableton_threads 
            WHERE thread_id = ?
        """,
            (thread_id,),
        )
        await db.commit()


async def thread_exists(thread_id: str) -> bool:
    """Check if a thread is registered in our tracking table."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            """
            SELECT 1 FROM ableton_threads WHERE thread_id = ?
        """,
            (thread_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def get_thread_message_count(thread_id: str) -> int:
    """Get the current message count for a thread."""
    db_path = await get_db_path()

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            """
            SELECT message_count FROM ableton_threads WHERE thread_id = ?
        """,
            (thread_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
