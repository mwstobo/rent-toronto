"""Scrape Kijiji for apartment adverts"""
import asyncio
import hashlib
import logging
import math
import re
from typing import Awaitable, Dict, List, NamedTuple, Optional, Tuple

import aiohttp
import bs4
import geopy.geocoders

import cache
import config

BASE_URL = "http://www.kijiji.ca"
AD_ID_REGEX = re.compile(r"\d{10}")
IMAGE_REGEX = re.compile(r"heroImageForPrint-*")
PRICE_REGEX = re.compile(r"^currentPrice-*")
TITLE_REGEX = re.compile(r"^title-*")
SPONSORED_CLASS = "top-feature"

UNIT_TYPES = {
    "bc": "b-bachelor-studio-apartments-condos/city-of-toronto/{}c211l1700273",
    "1b": "b-1-bedroom-apartments-condos/city-of-toronto/{}c212l1700273",
    "1b+d": "b-1-bedroom-den-apartments-condos/city-of-toronto/{}c213l1700273",
    "2b": "b-2-bedroom-apartments-condos/city-of-toronto/{}c214l1700273",
    "3b": "b-3-bedroom-apartments-condos/city-of-toronto/{}c215l1700273",
    "4b+": "b-4-plus-bedroom-apartments-condos/city-of-toronto/{}c216l1700273",
    "hs": "b-house-rental/city-of-toronto/{}c43l1700273",
}

LOCATOR = geopy.geocoders.GoogleV3(api_key=config.GOOGLE_GEO_API_KEY)
EARTH_RADIUS = 6371.0

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


class Advert(NamedTuple):
    """Represents an Apartment advert"""
    # TODO: proper types
    advert_id: str
    address: str
    category: str
    coordinates: Tuple[float, float]
    distance: float
    img_hash: str
    info_hash: str
    price: str
    title: str
    url: str


def build_page_urls() -> Dict[str, List[str]]:
    """Build a list of URLs for the Kijiji pages that list adverts"""
    urls: Dict[str, List[str]] = {}
    for category, frag in UNIT_TYPES.items():
        if category not in config.SELECTED_UNIT_TYPES:
            continue

        urls[category] = []
        for page in range(config.MAX_PAGES):
            page_frag: str = frag.format("page-{}/".format(page + 1))
            if page == 0:
                page_frag = frag.format("")
            url: str = "{}/{}".format(BASE_URL, page_frag)
            url += "r{}".format(config.SEARCH_DISTANCE)
            url += "?ad=offering"
            url += "&minNumberOfImages=2"
            url += "&price={}__{}".format(config.MIN_PRICE, config.MAX_PRICE)
            url += "&address={}".format(config.POSTAL)
            url += "&ll={},{}".format(config.POSTAL_LAT, config.POSTAL_LON)
            urls[category].append(url)
    return urls


async def open_url(url: str) -> bytes:
    """Open a url and return the bytes"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


def parse_advert_urls(html: bytes) -> List[str]:
    """Return a list of advert URLs from a Kijiji list page"""
    urls: List[str] = []
    soup = bs4.BeautifulSoup(html, "html.parser")
    adverts = soup.findAll("div", {"data-ad-id": AD_ID_REGEX})
    for advert in adverts:
        if SPONSORED_CLASS in advert["class"]:
            continue
        url = "{}{}".format(BASE_URL, advert["data-vip-url"].split("?src=")[0])
        urls.append(url)
    return urls


def get_coords(address: str) -> Tuple[float, float]:
    """Given an address, return the coordinates"""
    location = LOCATOR.geocode(address)
    return (location.longitude, location.latitude)


def get_distance(
        p1_deg: Tuple[float, float], p2_deg: Tuple[float, float]) -> float:
    """Get the distance in km between two points on the Earth.

    The two points are defined by latitude and longitude.
    See the haversine formula for more info."""
    p1_rad = (math.radians(p1_deg[0]), math.radians(p1_deg[1]))
    p2_rad = (math.radians(p2_deg[0]), math.radians(p2_deg[1]))

    dist = math.cos(p1_rad[1]) * math.cos(p2_rad[1])
    dist *= math.pow(math.sin((p2_rad[0] - p1_rad[0])/2.0), 2)
    dist += math.pow(math.sin((p2_rad[1] - p1_rad[1])/2.0), 2)
    dist = math.sqrt(dist)
    dist = math.asin(dist)
    dist *= 2.0 * EARTH_RADIUS

    return dist


def get_hash(data: bytes) -> str:
    """Returns the sha256 of the given bytes"""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


async def parse_advert(
        advert_id: str,
        url: str,
        category: str,
        html: bytes) -> Optional[Advert]:
    """Return an Advert from a Kijiji advert page"""
    soup = bs4.BeautifulSoup(html, "html.parser")

    try:
        title: str = soup.find("h1", {"class": TITLE_REGEX}).get_text()
    except AttributeError:
        logging.error("No title found at %s", url)
        return None

    try:
        address: str = soup.find("span", {"itemprop": "address"}).get_text()
    except AttributeError:
        logging.error("No address found at %s", url)
        return None

    try:
        img_url = soup.find("img", {"class": IMAGE_REGEX})["src"]
    except AttributeError:
        logging.error("No image found at %s", url)
        return None
    img_future = open_url(img_url)

    price: str = soup.find("span", {"class": PRICE_REGEX}).get_text()

    coordinates: Tuple[float, float] = get_coords(address)
    distance: float = get_distance(
        coordinates, (config.POSTAL_LON, config.POSTAL_LAT))

    img_hash: str = get_hash(await img_future)
    if cache.contains_info(img_hash):
        cache.add_ids([advert_id])
        logging.info("Duplicated advert image on %s. Skipping", advert_id)
        return None

    info_hash: str = get_hash("{}{}".format(title, address).encode("utf-8"))
    if cache.contains_info(info_hash):
        cache.add_ids([advert_id])
        logging.info("Duplicated advert info on %s. Skipping", advert_id)
        return None

    return Advert(advert_id=advert_id,
                  address=address,
                  category=category,
                  coordinates=coordinates,
                  distance=distance,
                  img_hash=img_hash,
                  info_hash=info_hash,
                  price=price,
                  title=title,
                  url=url)


async def get_advert_from_url(
        advert_url: str, category: str) -> Optional[Advert]:
    """Returns an Advert from a Kijiji advert page"""
    logging.info("Parsing %s", advert_url)
    advert_contents: bytes = await open_url(advert_url)
    advert_id = advert_url.split("/")[-1]

    return await parse_advert(advert_id, advert_url, category, advert_contents)


async def get_adverts_for_page(
        page_url: str, category: str) -> List[Optional[Advert]]:
    """Returns a list of Adverts from a Kijiji list page"""
    logging.info("Getting adverts from %s", page_url)
    page_contents: bytes = await open_url(page_url)
    advert_urls: List[str] = parse_advert_urls(page_contents)

    advert_futures: List[Awaitable[Optional[Advert]]] = []
    for advert_url in advert_urls:
        advert_id = advert_url.split("/")[-1]
        if cache.contains_id(advert_id):
            logging.info("Advert %s already saved", advert_id)
            continue
        advert_futures.append(get_advert_from_url(advert_url, category))

    adverts: List[Optional[Advert]] = await asyncio.gather(*advert_futures)
    return adverts


def get_adverts() -> List[Advert]:
    """Get a list of ads"""
    loop = asyncio.get_event_loop()
    logging.info("Starting advert fetch")

    category_urls: Dict[str, List[str]] = build_page_urls()
    adverts_futures: List[Awaitable[List[Optional[Advert]]]] = []
    for category, page_urls in category_urls.items():
        for page_url in page_urls:
            adverts_futures.append(get_adverts_for_page(page_url, category))

    adverts: List[Advert] = []
    for page in loop.run_until_complete(asyncio.gather(*adverts_futures)):
        adverts += filter(None.__ne__, page)

    logging.info("Advert fetch complete")
    return adverts
