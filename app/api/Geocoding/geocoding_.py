from geopy.geocoders import Nominatim
import geocoder
from .config import *

def get_addr():
    g = geocoder.ip(IP_LOC)
    latlng = g.latlng

    if not g.ok:
        return None
    
    geolocator = Nominatim(user_agent=APPLICATION_NAME)
    location = geolocator.reverse(latlng, language=LANGUAGE)

    return location.address
