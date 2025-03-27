import googlemaps
import logging
from shapely.geometry import Point
import environ
logger = logging.getLogger(__name__)

def lookup_address(address):
    env = environ.Env()
    googlemapkey = env.str('GOOGLE_MAPS_API_KEY')
    gmaps = googlemaps.Client(key=googlemapkey)
    logger.info("Looking up {} on Google maps".format(address))
    # Geocoding an address
    geocode_result = gmaps.geocode(address)
    if len(geocode_result)>0:
        geo=geocode_result[0]['geometry']
        logger.info("Found at geo {}".format(geo))
        p=Point(geo['location']['lng'], geo['location']['lat'])
        return p
    return None