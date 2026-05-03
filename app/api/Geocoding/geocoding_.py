from geopy.geocoders import Nominatim
import geocoder
from app.redis.redis_func import *
from app.util.general_utils import *
from .config import *
import json
from flask import session

def get_addr():
    """
    Returns the user's current address by IP lookup, pulling from Redis cache if available.
    Returns:
        str | None: A human-readable address string, or None if the IP lookup fails.
    """
    id = int(json.loads(session["profile_info"])["id"])
    key = f"{id}{REDIS_USER_ADDR_KEY_FORMAT}"

    val = redis_get(key)
    
    if val is not None:
        return val
    
    g = geocoder.ip(IP_LOC)
    latlng = g.latlng

    if not g.ok:
        return None

    geolocator = Nominatim(user_agent=APPLICATION_NAME)
    location = geolocator.reverse(latlng, language=LANGUAGE)
    addr = location.address

    redis_set(key, addr)
    
    return addr
