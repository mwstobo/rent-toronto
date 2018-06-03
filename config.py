"""Configuration options for the use throughout the program"""
import os

# Scraping
MAX_PAGES = int(os.environ.get("MAX_PAGES", 5))
MIN_PRICE = os.environ.get("MIN_PRICE", "1500")
MAX_PRICE = os.environ.get("MAX_PRICE", "3000")
POSTAL = os.environ.get("POSTAL", "M5J1E6")
POSTAL_LAT = float(os.environ.get("POSTAL_LAT", 43.645100))
POSTAL_LON = float(os.environ.get("POSTAL_LON", -79.381576))
SEARCH_DISTANCE = os.environ.get("SEARCH_DISTANCE", "5")
GOOGLE_GEO_API_KEY = os.environ.get("GOOGLE_GEO_API_KEY")
SELECTED_UNIT_TYPES = os.environ.get("SELECTED_UNIT_TYPES", "bc,1b").split(",")

# Email
FROM_ADDRESS = os.environ.get("FROM_ADDRESS", "")
TO_ADDRESSES = os.environ.get("TO_ADDRESSES", "").split(",")

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")


def _validate_presence(value):
    if not value:
        raise ValueError("{} must be set".format(value))


def validate() -> None:
    """Validate the current config options"""
    _validate_presence(GOOGLE_GEO_API_KEY)
    _validate_presence(TO_ADDRESSES)
