"""Collect various apartment adverts and check if they fall with an area"""
import sys
from typing import List

import alert
import area
import cache
import config
import scraper


def usage() -> None:
    """Print usage and exit"""
    print("Usage: {} KML_FILENAME".format(sys.argv[0]))
    sys.exit(1)

def main(kml_filename: str) -> None:
    """Main entry point to the program"""
    config.validate()

    area_checks: List[area.AreaCheck] = area.get_area_checks(kml_filename)
    adverts: List[scraper.Advert] = scraper.get_adverts()

    matched_adverts: List[scraper.Advert] = []
    for advert in adverts:
        for check in area_checks:
            if check(advert.coordinates):
                matched_adverts.append(advert)
    if matched_adverts:
        alert.send(matched_adverts)

    if adverts:
        cache.add_ids(list(map(lambda a: a.advert_id, adverts)))
        cache.add_info(list(map(lambda a: a.info_hash, adverts)))
        cache.add_info(list(map(lambda a: a.img_hash, adverts)))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    KML_FILENAME = sys.argv[1]
    main(KML_FILENAME)
