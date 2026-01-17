import argparse
import sys
import os
import logging
from typing import List, Optional

from downloader.factory import DownloaderFactory
from downloader.base import DownloadOptions, DownloadResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="CoomerDL Command Line Interface")

    # Core arguments
    parser.add_argument("urls", nargs="*", help="URLs to download")
    parser.add_argument("--batch-file", "-i", help="File containing URLs to download (one per line)")

    # Output options
    parser.add_argument("--output", "-o", default="downloads", help="Output directory (default: downloads)")

    # Filter options
    parser.add_argument("--no-images", action="store_true", help="Skip downloading images")
    parser.add_argument("--no-videos", action="store_true", help="Skip downloading videos")
    parser.add_argument("--no-compressed", action="store_true", help="Skip downloading compressed files")
    parser.add_argument("--no-documents", action="store_true", help="Skip downloading documents")

    # Advanced filters
    parser.add_argument("--min-size", type=str, help="Minimum file size (e.g. 5M, 100K)")
    parser.add_argument("--max-size", type=str, help="Maximum file size (e.g. 1G)")
    parser.add_argument("--date-from", help="Download only after this date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="Download only before this date (YYYY-MM-DD)")

    # Network options
    parser.add_argument("--proxy", help="Proxy URL (http://user:pass@host:port)")
    parser.add_argument("--user-agent", help="Custom User-Agent")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries per file")

    # Execution mode
    parser.add_argument("--headless", action="store_true", help="Force headless backend server mode (no GUI, no CLI download)")

    return parser.parse_args()

def parse_size(size_str: str) -> int:
    """Parse size string to bytes."""
    if not size_str:
        return 0

    units = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    size_str = size_str.upper()

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                return int(float(size_str[:-1]) * multiplier)
            except ValueError:
                return 0
    try:
        return int(size_str)
    except ValueError:
        return 0

def run_cli():
    """Main CLI entry point."""
    args = parse_args()

    # If headless flag is set, return False to let main.py start the server
    if args.headless:
        return False

    # If no URLs and no batch file, return False to let main.py start the GUI
    if not args.urls and not args.batch_file:
        return False

    # Otherwise, run CLI download
    print("CoomerDL CLI Mode")
    print("-----------------")

    # Collect URLs
    urls = list(args.urls)
    if args.batch_file:
        if os.path.exists(args.batch_file):
            with open(args.batch_file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"Error: Batch file not found: {args.batch_file}")
            sys.exit(1)

    if not urls:
        print("No URLs provided.")
        return True # Handled, exit

    # Configure options
    options = DownloadOptions(
        download_images=not args.no_images,
        download_videos=not args.no_videos,
        download_compressed=not args.no_compressed,
        download_documents=not args.no_documents,
        min_file_size=parse_size(args.min_size),
        max_file_size=parse_size(args.max_size),
        date_from=args.date_from,
        date_to=args.date_to,
        proxy_url=args.proxy if args.proxy else "",
        proxy_type="custom" if args.proxy else "none",
        user_agent=args.user_agent,
        max_retries=args.max_retries
    )

    # Process URLs
    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        print(f"\nProcessing [{i}/{len(urls)}]: {url}")

        try:
            downloader = DownloaderFactory.get_downloader(
                url=url,
                download_folder=args.output,
                options=options,
                log_callback=lambda msg: logger.info(msg)
            )

            if not downloader:
                print(f"Error: No supported downloader found for {url}")
                fail_count += 1
                continue

            print(f"Using downloader: {downloader.get_site_name()}")
            result = downloader.download(url)

            if result.success:
                print(f"Success: {result.completed_files} files downloaded.")
                success_count += 1
            else:
                print(f"Failed: {result.error_message}")
                fail_count += 1

        except Exception as e:
            print(f"Error processing URL: {e}")
            fail_count += 1

    print("\n-----------------")
    print(f"Batch Complete. Success: {success_count}, Failed: {fail_count}")

    return True
