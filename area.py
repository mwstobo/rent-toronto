"""Methods relating to areas in the world"""
import functools
from typing import Any, Callable, List, Tuple

import fastkml
import shapely.geometry

AreaCheck = Callable[[Tuple[float, float]], bool]


def contains_point(polygon: Any, coords: Tuple[float, float]) -> bool:
    """Check if this polygon contains a given point"""
    point = shapely.geometry.Point(coords[0], coords[1])
    return polygon.contains(point)


def get_area_checks(kml_filename: str) -> List[AreaCheck]:
    """Read in a KML file and return a list of Polygons defined within"""
    kml = fastkml.kml.KML()
    with open(kml_filename, "r") as kml_file:
        content = kml_file.read()
        kml.from_string(content)

    checks: List[AreaCheck] = []
    for document in kml.features():
        for placemark in document.features():
            check = functools.partial(contains_point, placemark.geometry)
            checks.append(check)

    return checks
