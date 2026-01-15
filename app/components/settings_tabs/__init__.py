"""Settings tabs package."""
from __future__ import annotations

from app.components.settings_tabs.logging_settings import LoggingSettingsTab
from app.components.settings_tabs.scraper_settings import ScraperSettingsTab
from app.components.settings_tabs.network_settings import NetworkSettingsTab
from app.components.settings_tabs.filters_settings import FiltersSettingsTab

__all__ = ['LoggingSettingsTab', 'ScraperSettingsTab', 'NetworkSettingsTab', 'FiltersSettingsTab']
