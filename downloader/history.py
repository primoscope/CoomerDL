"""
Download History Database - Persistent storage for jobs and events.

Uses SQLite for thread-safe persistence of download history.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from typing import List, Optional, Dict
from pathlib import Path

from downloader.models import (
    DownloadJob, DownloadEvent, JobStatus, DownloadEventType
)


class DownloadHistoryDB:
    """
    SQLite-based persistent storage for download jobs and events.
    
    Thread-safe implementation using a lock for all database operations.
    """
    
    DEFAULT_DB_PATH = "resources/config/download_history.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the history database.
        
        Args:
            db_path: Path to the SQLite database file.
                     Defaults to resources/config/download_history.db
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Jobs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        url TEXT NOT NULL,
                        engine TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        finished_at TEXT,
                        total_items INTEGER DEFAULT 0,
                        completed_items INTEGER DEFAULT 0,
                        failed_items INTEGER DEFAULT 0,
                        skipped_items INTEGER DEFAULT 0,
                        output_folder TEXT,
                        error_message TEXT,
                        options_json TEXT
                    )
                ''')
                
                # Events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        type TEXT NOT NULL,
                        payload_json TEXT,
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                    )
                ''')
                
                # Job items table for crash-resume
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS job_items (
                        job_id TEXT NOT NULL,
                        item_key TEXT NOT NULL,
                        status TEXT NOT NULL,
                        file_path TEXT,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY (job_id, item_key),
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                    )
                ''')
                
                # Create indexes for common queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_jobs_status 
                    ON jobs(status)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_jobs_created_at 
                    ON jobs(created_at DESC)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_events_job_id 
                    ON events(job_id)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_job_items_job_id 
                    ON job_items(job_id)
                ''')
                
                conn.commit()
            finally:
                conn.close()
    
    def save_job(self, job: DownloadJob) -> None:
        """
        Save or update a job in the database.
        
        Args:
            job: The job to save.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO jobs (
                        job_id, url, engine, status, created_at, started_at,
                        finished_at, total_items, completed_items, failed_items,
                        skipped_items, output_folder, error_message, options_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.id,
                    job.url,
                    job.engine,
                    job.status.value,
                    job.created_at,
                    job.started_at,
                    job.finished_at,
                    job.total_items,
                    job.completed_items,
                    job.failed_items,
                    job.skipped_items,
                    job.output_folder,
                    job.error_message,
                    json.dumps(job.options_snapshot)
                ))
                
                conn.commit()
            finally:
                conn.close()
    
    def append_event(self, event: DownloadEvent) -> None:
        """
        Append an event to the database.
        
        Args:
            event: The event to append.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO events (job_id, timestamp, type, payload_json)
                    VALUES (?, ?, ?, ?)
                ''', (
                    event.job_id,
                    event.timestamp,
                    event.type.value,
                    json.dumps(event.payload)
                ))
                
                conn.commit()
            finally:
                conn.close()
    
    def list_jobs(
        self,
        limit: int = 200,
        status: Optional[JobStatus] = None,
        offset: int = 0
    ) -> List[DownloadJob]:
        """
        List jobs from the database.
        
        Args:
            limit: Maximum number of jobs to return.
            status: Filter by status (optional).
            offset: Number of jobs to skip for pagination.
            
        Returns:
            List of DownloadJob instances.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if status:
                    cursor.execute('''
                        SELECT * FROM jobs 
                        WHERE status = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    ''', (status.value, limit, offset))
                else:
                    cursor.execute('''
                        SELECT * FROM jobs 
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    ''', (limit, offset))
                
                rows = cursor.fetchall()
                return [self._row_to_job(row) for row in rows]
            finally:
                conn.close()
    
    def get_job(self, job_id: str) -> Optional[DownloadJob]:
        """
        Get a specific job by ID.
        
        Args:
            job_id: The job ID to look up.
            
        Returns:
            DownloadJob if found, None otherwise.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT * FROM jobs WHERE job_id = ?',
                    (job_id,)
                )
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_job(row)
                return None
            finally:
                conn.close()
    
    def get_job_events(
        self,
        job_id: str,
        limit: int = 1000
    ) -> List[DownloadEvent]:
        """
        Get events for a specific job.
        
        Args:
            job_id: The job ID to look up events for.
            limit: Maximum number of events to return.
            
        Returns:
            List of DownloadEvent instances.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM events 
                    WHERE job_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (job_id, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_event(row) for row in rows]
            finally:
                conn.close()
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and its events from the database.
        
        Args:
            job_id: The job ID to delete.
            
        Returns:
            True if job was deleted, False if not found.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Delete job items first (foreign key)
                cursor.execute(
                    'DELETE FROM job_items WHERE job_id = ?',
                    (job_id,)
                )
                
                # Delete events (foreign key)
                cursor.execute(
                    'DELETE FROM events WHERE job_id = ?',
                    (job_id,)
                )
                
                # Delete job
                cursor.execute(
                    'DELETE FROM jobs WHERE job_id = ?',
                    (job_id,)
                )
                
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
            finally:
                conn.close()
    
    # =========================================================================
    # Job Items API (for crash-resume)
    # =========================================================================
    
    def mark_job_item_done(
        self,
        job_id: str,
        item_key: str,
        file_path: str,
        status: str = "completed"
    ) -> None:
        """
        Mark a job item as completed/skipped/failed.
        
        Args:
            job_id: The job ID.
            item_key: Unique identifier for the item (canonical URL or ID).
            file_path: Local path where the file was saved.
            status: Status string (completed, skipped, failed).
        """
        from datetime import datetime, timezone
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO job_items 
                    (job_id, item_key, status, file_path, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    job_id,
                    item_key,
                    status,
                    file_path,
                    datetime.now(timezone.utc).isoformat()
                ))
                
                conn.commit()
            finally:
                conn.close()
    
    def get_job_items(self, job_id: str) -> List[Dict[str, str]]:
        """
        Get all items for a job.
        
        Args:
            job_id: The job ID.
            
        Returns:
            List of item dictionaries with keys: item_key, status, file_path.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_key, status, file_path, updated_at
                    FROM job_items
                    WHERE job_id = ?
                ''', (job_id,))
                
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def get_completed_item_keys(self, job_id: str) -> set:
        """
        Get set of completed item keys for a job.
        
        Useful for resume logic - skip items already done.
        
        Args:
            job_id: The job ID.
            
        Returns:
            Set of item keys that are completed or skipped.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_key FROM job_items
                    WHERE job_id = ? AND status IN ('completed', 'skipped')
                ''', (job_id,))
                
                return {row[0] for row in cursor.fetchall()}
            finally:
                conn.close()
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        error_message: Optional[str] = None,
        counters: Optional[Dict[str, int]] = None
    ) -> bool:
        """
        Update job status and optionally other fields.
        
        Args:
            job_id: The job ID.
            status: New status string.
            started_at: Optional started timestamp.
            finished_at: Optional finished timestamp.
            error_message: Optional error message.
            counters: Optional dict with total_items, completed_items, etc.
            
        Returns:
            True if job was updated, False if not found.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Build update query dynamically
                updates = ['status = ?']
                params = [status]
                
                if started_at is not None:
                    updates.append('started_at = ?')
                    params.append(started_at)
                
                if finished_at is not None:
                    updates.append('finished_at = ?')
                    params.append(finished_at)
                
                if error_message is not None:
                    updates.append('error_message = ?')
                    params.append(error_message)
                
                if counters:
                    for key in ['total_items', 'completed_items', 'failed_items', 'skipped_items']:
                        if key in counters:
                            updates.append(f'{key} = ?')
                            params.append(counters[key])
                
                params.append(job_id)
                
                cursor.execute(
                    f'UPDATE jobs SET {", ".join(updates)} WHERE job_id = ?',
                    params
                )
                
                updated = cursor.rowcount > 0
                conn.commit()
                return updated
            finally:
                conn.close()
    
    def get_resumable_jobs(self) -> List[DownloadJob]:
        """
        Get jobs that were interrupted and can be resumed.
        
        Returns jobs in RUNNING or PENDING state.
        
        Returns:
            List of jobs that can be resumed.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM jobs 
                    WHERE status IN ('running', 'pending')
                    ORDER BY created_at ASC
                ''')
                
                return [self._row_to_job(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def clear_completed_jobs(self, keep_last: int = 100) -> int:
        """
        Clear old completed jobs, keeping the most recent ones.
        
        Args:
            keep_last: Number of completed jobs to keep.
            
        Returns:
            Number of jobs deleted.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Get IDs of jobs to delete
                cursor.execute('''
                    SELECT job_id FROM jobs 
                    WHERE status = ?
                    ORDER BY finished_at DESC
                    LIMIT -1 OFFSET ?
                ''', (JobStatus.COMPLETED.value, keep_last))
                
                job_ids = [row[0] for row in cursor.fetchall()]
                
                if not job_ids:
                    return 0
                
                # Delete events
                placeholders = ','.join('?' * len(job_ids))
                cursor.execute(
                    f'DELETE FROM events WHERE job_id IN ({placeholders})',
                    job_ids
                )
                
                # Delete jobs
                cursor.execute(
                    f'DELETE FROM jobs WHERE job_id IN ({placeholders})',
                    job_ids
                )
                
                deleted = len(job_ids)
                conn.commit()
                return deleted
            finally:
                conn.close()
    
    def get_stats(self) -> dict:
        """
        Get statistics about the download history.
        
        Returns:
            Dictionary with counts by status.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM jobs 
                    GROUP BY status
                ''')
                
                stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('SELECT COUNT(*) FROM jobs')
                stats['total'] = cursor.fetchone()[0]
                
                return stats
            finally:
                conn.close()
    
    def _row_to_job(self, row: sqlite3.Row) -> DownloadJob:
        """Convert a database row to a DownloadJob instance."""
        options = {}
        if row['options_json']:
            try:
                options = json.loads(row['options_json'])
            except json.JSONDecodeError:
                pass
        
        return DownloadJob(
            id=row['job_id'],
            url=row['url'],
            engine=row['engine'],
            status=JobStatus(row['status']),
            created_at=row['created_at'],
            started_at=row['started_at'],
            finished_at=row['finished_at'],
            total_items=row['total_items'],
            completed_items=row['completed_items'],
            failed_items=row['failed_items'],
            skipped_items=row['skipped_items'],
            output_folder=row['output_folder'] or '',
            error_message=row['error_message'],
            options_snapshot=options
        )
    
    def _row_to_event(self, row: sqlite3.Row) -> DownloadEvent:
        """Convert a database row to a DownloadEvent instance."""
        payload = {}
        if row['payload_json']:
            try:
                payload = json.loads(row['payload_json'])
            except json.JSONDecodeError:
                pass
        
        return DownloadEvent(
            type=DownloadEventType(row['type']),
            job_id=row['job_id'],
            timestamp=row['timestamp'],
            payload=payload
        )
