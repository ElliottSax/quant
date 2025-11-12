"""Base scraper abstract class."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class NavigationException(ScraperException):
    """Raised when navigation fails."""
    pass


class ParsingException(ScraperException):
    """Raised when parsing fails."""
    pass


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialize scraper.

        Args:
            headless: Run browser in headless mode
            timeout: Default timeout for element waits (seconds)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver: webdriver.Chrome | None = None
        self.wait: WebDriverWait | None = None

    def _setup_driver(self) -> None:
        """Configure and initialize Chrome WebDriver."""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless=new")

            # Security and stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            # Privacy options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # User agent to appear as normal browser
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # Window size for consistent rendering
            chrome_options.add_argument("--window-size=1920,1080")

            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, self.timeout)

            logger.info("Chrome WebDriver initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}", exc_info=True)
            raise ScraperException(f"WebDriver initialization failed: {e}")

    def _teardown_driver(self) -> None:
        """Clean up and close WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None

    def _retry_on_failure(self, func, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            ScraperException: If all retries fail
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.max_retries} for {func.__name__}")
                return func(*args, **kwargs)

            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed for {func.__name__}: {e}"
                )

                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {func.__name__}")

            except Exception as e:
                # Non-recoverable errors should not be retried
                logger.error(f"Non-recoverable error in {func.__name__}: {e}", exc_info=True)
                raise ScraperException(f"Scraping failed: {e}")

        # If we get here, all retries failed
        raise ScraperException(
            f"Failed after {self.max_retries} attempts. Last error: {last_exception}"
        )

    @abstractmethod
    def scrape(self) -> list[dict[str, Any]]:
        """
        Main scraping method to be implemented by subclasses.

        Returns:
            List of dictionaries containing scraped trade data

        Raises:
            ScraperException: If scraping fails
        """
        pass

    @abstractmethod
    def _navigate_to_source(self) -> None:
        """Navigate to the data source website."""
        pass

    @abstractmethod
    def _extract_data(self) -> list[dict[str, Any]]:
        """Extract trade data from the website."""
        pass

    def run(self) -> list[dict[str, Any]]:
        """
        Execute the full scraping workflow with setup and teardown.

        Returns:
            List of scraped trade data dictionaries

        Raises:
            ScraperException: If scraping fails
        """
        try:
            logger.info(f"Starting {self.__class__.__name__} scraping workflow")
            start_time = datetime.now(timezone.utc)

            # Setup
            self._setup_driver()

            # Execute scraping
            data = self.scrape()

            # Calculate duration
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"{self.__class__.__name__} completed successfully. "
                f"Scraped {len(data)} records in {duration:.2f}s"
            )

            return data

        except Exception as e:
            logger.error(f"{self.__class__.__name__} failed: {e}", exc_info=True)
            raise

        finally:
            # Always cleanup
            self._teardown_driver()

    def __enter__(self):
        """Context manager entry."""
        self._setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._teardown_driver()
        return False  # Don't suppress exceptions
