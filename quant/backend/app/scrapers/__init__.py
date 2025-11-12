"""Web scrapers for congressional trading data."""

from app.scrapers.base import BaseScraper
from app.scrapers.senate import SenateScraper
from app.scrapers.house import HouseScraper

__all__ = ["BaseScraper", "SenateScraper", "HouseScraper"]
