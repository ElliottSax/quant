"""Web scrapers for congressional trading data."""

from app.scrapers.base import BaseScraper
from app.scrapers.senate import SenateScraper

__all__ = ["BaseScraper", "SenateScraper"]
