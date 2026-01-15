"""
Download scheduler module.

Provides functionality for scheduling downloads at specific times or intervals.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, List, Dict, Any
import threading
import time
import json
import sqlite3
from pathlib import Path


class ScheduleType(Enum):
    """Type of schedule."""
    ONCE = "once"  # Run once at specific time
    DAILY = "daily"  # Run daily at specific time
    WEEKLY = "weekly"  # Run weekly on specific day/time
    INTERVAL = "interval"  # Run at fixed intervals


class ScheduleStatus(Enum):
    """Status of a scheduled job."""
    PENDING = "pending"  # Waiting to run
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed to execute
    CANCELLED = "cancelled"  # Cancelled by user
    PAUSED = "paused"  # Temporarily paused


@dataclass
class ScheduledJob:
    """A scheduled download job."""
    id: Optional[int] = None
    name: str = ""
    url: str = ""
    download_folder: str = ""
    schedule_type: ScheduleType = ScheduleType.ONCE
    next_run: Optional[datetime] = None
    interval_minutes: int = 60  # For INTERVAL type
    time_of_day: Optional[str] = None  # "HH:MM" for DAILY/WEEKLY
    day_of_week: Optional[int] = None  # 0=Monday for WEEKLY
    status: ScheduleStatus = ScheduleStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    run_count: int = 0
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'download_folder': self.download_folder,
            'schedule_type': self.schedule_type.value,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'interval_minutes': self.interval_minutes,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count,
            'enabled': self.enabled,
            'options': self.options
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScheduledJob:
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            name=data['name'],
            url=data['url'],
            download_folder=data['download_folder'],
            schedule_type=ScheduleType(data['schedule_type']),
            next_run=datetime.fromisoformat(data['next_run']) if data.get('next_run') else None,
            interval_minutes=data.get('interval_minutes', 60),
            time_of_day=data.get('time_of_day'),
            day_of_week=data.get('day_of_week'),
            status=ScheduleStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
            run_count=data.get('run_count', 0),
            enabled=data.get('enabled', True),
            options=data.get('options', {})
        )


class DownloadScheduler:
    """
    Manages scheduled downloads.
    
    Persists schedules to SQLite and runs downloads at specified times.
    """
    
    def __init__(
        self,
        db_path: str = "resources/config/scheduler.db",
        on_job_due: Optional[Callable[[ScheduledJob], None]] = None
    ):
        """
        Initialize the scheduler.
        
        Args:
            db_path: Path to SQLite database for persistence
            on_job_due: Callback when a job is due to run
        """
        self.db_path = Path(db_path)
        self.on_job_due = on_job_due
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    download_folder TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    next_run TEXT,
                    interval_minutes INTEGER,
                    time_of_day TEXT,
                    day_of_week INTEGER,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    last_run TEXT,
                    run_count INTEGER DEFAULT 0,
                    enabled INTEGER DEFAULT 1,
                    options TEXT
                )
            """)
            conn.commit()
    
    def add_job(self, job: ScheduledJob) -> int:
        """
        Add a scheduled job.
        
        Args:
            job: The job to schedule
            
        Returns:
            The job ID
        """
        with self._lock:
            # Calculate next run time
            if job.next_run is None:
                job.next_run = self._calculate_next_run(job)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO scheduled_jobs (
                        name, url, download_folder, schedule_type, next_run,
                        interval_minutes, time_of_day, day_of_week, status,
                        created_at, enabled, options
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.name,
                    job.url,
                    job.download_folder,
                    job.schedule_type.value,
                    job.next_run.isoformat() if job.next_run else None,
                    job.interval_minutes,
                    job.time_of_day,
                    job.day_of_week,
                    job.status.value,
                    job.created_at.isoformat(),
                    1 if job.enabled else 0,
                    json.dumps(job.options)
                ))
                conn.commit()
                job.id = cursor.lastrowid
                return job.id
    
    def remove_job(self, job_id: int) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            True if job was removed, False if not found
        """
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM scheduled_jobs WHERE id = ?",
                    (job_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
    
    def update_job(self, job: ScheduledJob) -> bool:
        """
        Update a scheduled job.
        
        Args:
            job: The job to update (must have id set)
            
        Returns:
            True if job was updated, False if not found
        """
        if job.id is None:
            return False
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE scheduled_jobs SET
                        name = ?, url = ?, download_folder = ?, schedule_type = ?,
                        next_run = ?, interval_minutes = ?, time_of_day = ?,
                        day_of_week = ?, status = ?, last_run = ?, run_count = ?,
                        enabled = ?, options = ?
                    WHERE id = ?
                """, (
                    job.name,
                    job.url,
                    job.download_folder,
                    job.schedule_type.value,
                    job.next_run.isoformat() if job.next_run else None,
                    job.interval_minutes,
                    job.time_of_day,
                    job.day_of_week,
                    job.status.value,
                    job.last_run.isoformat() if job.last_run else None,
                    job.run_count,
                    1 if job.enabled else 0,
                    json.dumps(job.options),
                    job.id
                ))
                conn.commit()
                return cursor.rowcount > 0
    
    def get_job(self, job_id: int) -> Optional[ScheduledJob]:
        """
        Get a scheduled job by ID.
        
        Args:
            job_id: ID of the job
            
        Returns:
            The job or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scheduled_jobs WHERE id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_job(row)
        return None
    
    def get_all_jobs(self) -> List[ScheduledJob]:
        """
        Get all scheduled jobs.
        
        Returns:
            List of all jobs
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM scheduled_jobs ORDER BY next_run")
            return [self._row_to_job(row) for row in cursor.fetchall()]
    
    def get_enabled_jobs(self) -> List[ScheduledJob]:
        """
        Get all enabled jobs.
        
        Returns:
            List of enabled jobs
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scheduled_jobs WHERE enabled = 1 ORDER BY next_run"
            )
            return [self._row_to_job(row) for row in cursor.fetchall()]
    
    def _row_to_job(self, row: sqlite3.Row) -> ScheduledJob:
        """Convert database row to ScheduledJob."""
        return ScheduledJob(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            download_folder=row['download_folder'],
            schedule_type=ScheduleType(row['schedule_type']),
            next_run=datetime.fromisoformat(row['next_run']) if row['next_run'] else None,
            interval_minutes=row['interval_minutes'],
            time_of_day=row['time_of_day'],
            day_of_week=row['day_of_week'],
            status=ScheduleStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_run=datetime.fromisoformat(row['last_run']) if row['last_run'] else None,
            run_count=row['run_count'],
            enabled=bool(row['enabled']),
            options=json.loads(row['options']) if row['options'] else {}
        )
    
    def _calculate_next_run(self, job: ScheduledJob) -> datetime:
        """Calculate the next run time for a job."""
        now = datetime.now()
        
        if job.schedule_type == ScheduleType.ONCE:
            # Run immediately or at specified time
            return job.next_run or now
        
        elif job.schedule_type == ScheduleType.INTERVAL:
            # Run after interval
            return now + timedelta(minutes=job.interval_minutes)
        
        elif job.schedule_type == ScheduleType.DAILY:
            # Run daily at specified time
            if not job.time_of_day:
                return now + timedelta(days=1)
            
            hour, minute = map(int, job.time_of_day.split(':'))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif job.schedule_type == ScheduleType.WEEKLY:
            # Run weekly on specific day/time
            if not job.time_of_day or job.day_of_week is None:
                return now + timedelta(weeks=1)
            
            hour, minute = map(int, job.time_of_day.split(':'))
            
            # Find next occurrence of the day
            days_ahead = job.day_of_week - now.weekday()
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            elif days_ahead == 0:  # Today
                target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target_time <= now:
                    days_ahead = 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_run
        
        return now
    
    def start(self) -> None:
        """Start the scheduler thread."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler thread."""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            self._stop_event.set()
            
            if self._thread:
                self._thread.join(timeout=5)
                self._thread = None
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running and not self._stop_event.is_set():
            try:
                self._check_due_jobs()
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
            
            # Sleep for 10 seconds or until stopped
            self._stop_event.wait(10)
    
    def _check_due_jobs(self) -> None:
        """Check for jobs that are due to run."""
        now = datetime.now()
        
        for job in self.get_enabled_jobs():
            if job.next_run and job.next_run <= now and job.status == ScheduleStatus.PENDING:
                # Job is due
                self._execute_job(job)
    
    def _execute_job(self, job: ScheduledJob) -> None:
        """Execute a scheduled job."""
        with self._lock:
            # Update status
            job.status = ScheduleStatus.RUNNING
            self.update_job(job)
        
        # Call callback
        if self.on_job_due:
            try:
                self.on_job_due(job)
            except Exception as e:
                print(f"Error executing job {job.id}: {e}")
                job.status = ScheduleStatus.FAILED
            else:
                job.status = ScheduleStatus.COMPLETED
        
        # Update job
        with self._lock:
            job.last_run = datetime.now()
            job.run_count += 1
            
            # Calculate next run for recurring jobs
            if job.schedule_type != ScheduleType.ONCE:
                job.next_run = self._calculate_next_run(job)
                job.status = ScheduleStatus.PENDING
            else:
                job.enabled = False  # Disable one-time jobs after execution
            
            self.update_job(job)
