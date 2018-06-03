# rent-toronto
Find apartment advertisements that are relevant to you. Just configure the
script with your criteria and receive emails with matching rental properties in
Toronto.

Here's how it works: advertisements are scraped from Kijiji based on provided
search criteria. Some of the basic criteria include price range, work location,
and relevant unit types. After discarding duplicate adverts, the geographic
coordinates are retrieved using the [Google Maps Geocoding API][Geocoding]. The
coordinates are tested against a provided [KML][KML] file to determine if they
fall within your range.  Any remaining adverts are sent to the provided email
addresses via [Amazon SES][SES].

Hopefully this will help save you from wading through pages and pages of
reposted and irrelevant advertisements when looking for a place to live.

The original idea for this project was inspired by
[toronto-apartment-finder][apartment-finder]. Please go check it out!

# Usage

## Prerequisites
* Python 3.6+, for type hinting
* Redis, for caching seen advertisements
* Google Maps Geocoding API key
* Amazon SES credentials

Also make sure to install the Python requirements:
```
pip install -r requirements.txt
```

## Running
```
python main.py kml_filename
```
If you're curious how to generate a KML file, you can use
[Google MyMaps][MyMaps] to draw and export your desired living area on a map.
Your KML file can contain multiple different polygons


## Configuring
This script is configured via environment variables. Here are the available
options:

### Required
Variable | Description
---------|------------
`GOOGLE_GEO_API_KEY` | API key for the Google Maps Geocoding API
`FROM_ADDRESS` | Email to send the alerts from
`TO_ADDRESSES` | Comma-separated list of email address to send the alerts to

### Kijiji Criteria
Variable | Description | Default
---------|-------------|---------
`POSTAL` | Postal code of your workplace (or any place you want to centre your search around) | `M5J1E6`
`POSTAL_LAT` | Latitude of the above postal code (saves a geocoding call) | `43.645100`
`POSTAL_LON` | Longitude of the above postal code | `-79.381576`
`SEARCH_DISTANCE` | Maximum distance to search from the above postal code, in km | `5`
`MAX_PAGES` | Number of Kijiji pages to search per unit type| `5`
`MIN_PRICE` | Minimum price for an advertisement | `1500`
`MAX_PRICE` | Maximum price for an advertisement | `3000`
`SELECTED_UNIT_TYPES` | Comma seperated list of unit types you want to search | `bc,1b`

Valid unit types are:

Unit type | Description
----------|------------
`bc` | Bachelor
`1b` | One bedroom
`1b+d` | One bedroom plus den
`2b` | Two bedrooms
`3b` | Three bedrooms
`4b+` | Four or more bedrooms
`hs` | House


### Redis
Variable | Description | Default
---------|-------------|--------
`REDIS_HOST` | Address where Redis is hosted | `localhost`

## Deploying
Feel free to use the provided Dockerfile to easily run this script in a
production environment.


[Geocoding]: https://developers.google.com/maps/documentation/geocoding/intro
[KML]: https://developers.google.com/kml/documentation/kml_tut
[SES]: https://aws.amazon.com/ses/
[apartment-finder]: https://github.com/ian-whitestone/toronto-apartment-finder
[MyMaps]: https://www.google.com/mymaps
