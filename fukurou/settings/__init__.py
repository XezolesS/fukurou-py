"""
A module for managing settings within the cogs.

The clients, channels or guilds can each have their own value of settings.
"""
from .interfaces import BaseSetting
from .service import CogSettingService, SettingService

__all__ = [
    'BaseSetting',
    'CogSettingService',
    'SettingService'
]