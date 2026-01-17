import asyncio
import logging
from backend.api.services.queue_service import QueueService, get_queue
from backend.api.services.download_service import DownloadService
from app.models.download_queue import QueueItemStatus
from backend.api.models.schemas import DownloadOptionsSchema

logger = logging.getLogger(__name__)

class QueueWorker:
    _is_running = False
    _task = None

    @classmethod
    def start(cls):
        if cls._is_running:
            return
        cls._is_running = True
        cls._task = asyncio.create_task(cls._run())
        logger.info("Queue worker started")

    @classmethod
    def stop(cls):
        cls._is_running = False
        if cls._task:
            cls._task.cancel()
        logger.info("Queue worker stopped")

    @classmethod
    async def _run(cls):
        logger.info("Queue worker loop running")
        while cls._is_running:
            try:
                # Basic concurrency check (max 2)
                active_count = len([
                    d for d in DownloadService.get_all_downloads().values()
                    if d["status"] == "downloading"
                ])

                if active_count < 2:
                    item = QueueService.get_next_pending()
                    if item:
                        logger.info(f"Processing queue item: {item.url}")
                        queue = get_queue()

                        # Convert options
                        options_schema = None
                        if item.options:
                            try:
                                options_schema = DownloadOptionsSchema(**item.options)
                            except Exception:
                                pass # Use defaults

                        # Update status to DOWNLOADING
                        queue.update_status(item.id, QueueItemStatus.DOWNLOADING)

                        try:
                            # Start download
                            await DownloadService.start_download(
                                url=item.url,
                                download_folder=item.download_folder,
                                options=options_schema
                            )
                            # Note: We are not tracking completion here.
                            # The item will remain in DOWNLOADING state in queue.json
                            # until manually cleared or handled by future sync logic.
                        except Exception as e:
                            logger.error(f"Failed to process item {item.id}: {e}")
                            queue.update_status(item.id, QueueItemStatus.FAILED, error_message=str(e))

            except Exception as e:
                logger.error(f"Error in queue worker: {e}")

            await asyncio.sleep(5)
