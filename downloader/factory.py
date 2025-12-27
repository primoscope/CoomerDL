"""
Factory for creating downloader instances based on URL.
"""
from typing import Optional, List, Type
from downloader.base import BaseDownloader, DownloadOptions


class DownloaderFactory:
    """
    Factory class for creating appropriate downloader based on URL.
    
    Usage:
        factory = DownloaderFactory()
        factory.register(CoomerDownloader)
        factory.register(EromeDownloader)
        
        downloader = factory.get_downloader(url, download_folder="/downloads")
        if downloader:
            result = downloader.download(url)
    """
    
    _downloader_classes: List[Type[BaseDownloader]] = []
    
    @classmethod
    def register(cls, downloader_class: Type[BaseDownloader]) -> Type[BaseDownloader]:
        """
        Register a downloader class. Can be used as decorator.
        
        Args:
            downloader_class: The downloader class to register
            
        Returns:
            The same class (for decorator usage)
        """
        if downloader_class not in cls._downloader_classes:
            cls._downloader_classes.append(downloader_class)
        return downloader_class
    
    @classmethod
    def get_downloader(
        cls,
        url: str,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        **kwargs
    ) -> Optional[BaseDownloader]:
        """
        Get appropriate downloader for the given URL.
        
        Args:
            url: The URL to find a downloader for
            download_folder: Path to save downloaded files
            options: Download configuration options
            **kwargs: Additional arguments passed to downloader constructor
            
        Returns:
            Appropriate downloader instance, or None if no match
        """
        for downloader_class in cls._downloader_classes:
            # Create temporary instance to check URL support
            instance = downloader_class(
                download_folder=download_folder,
                options=options,
                **kwargs
            )
            if instance.supports_url(url):
                return instance
        return None
    
    @classmethod
    def get_supported_sites(cls) -> List[str]:
        """
        Get list of all supported site names.
        
        Returns:
            List of site names from registered downloaders
        """
        sites = []
        for downloader_class in cls._downloader_classes:
            # Create minimal instance to get site name
            instance = downloader_class(download_folder="")
            sites.append(instance.get_site_name())
        return sites
    
    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered downloaders (useful for testing)."""
        cls._downloader_classes = []


# Auto-register downloaders
from downloader.bunkr import BunkrDownloader
from downloader.erome import EromeDownloader
from downloader.simpcity import SimpCityDownloader

DownloaderFactory.register(BunkrDownloader)
DownloaderFactory.register(EromeDownloader)
DownloaderFactory.register(SimpCityDownloader)
