"""
Módulo para funcionalidades relacionadas con Synology NAS.
"""

from .synology_client import SynologyClient
from .synology_uploader import SynologyUploader

__all__ = ['SynologyClient', 'SynologyUploader'] 