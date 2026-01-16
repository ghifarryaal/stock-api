import time

CACHE = {}
CACHE_TTL = 300

def get_cache(key):
    if key in CACHE:
        cached = CACHE[key]
        if time.time() - cached["time"] < CACHE_TTL:
            return cached["data"]
    return None

def set_cache(key, data):
    CACHE[key] = {
        "time": time.time(),
        "data": data
    }
