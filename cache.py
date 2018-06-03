"""Caching for advert ids"""
from typing import List

import redis

import config

REDIS_POOL = redis.ConnectionPool(host=config.REDIS_HOST, decode_responses=True)

ADVERT_IDS_KEY = "adverts"
ADVERT_INFO_KEY = "advert_info"


def contains_id(advert_id: str) -> bool:
    """Check if this advert is in the cache"""
    client = redis.StrictRedis(connection_pool=REDIS_POOL)
    return client.sismember(ADVERT_IDS_KEY, advert_id) == 1


def add_ids(advert_ids: List[str]) -> None:
    """Add the advert to the cache"""
    client = redis.StrictRedis(connection_pool=REDIS_POOL)
    client.sadd(ADVERT_IDS_KEY, *advert_ids)


def contains_info(advert_info: str) -> bool:
    """Check if this advert info hash is in the cache"""
    client = redis.StrictRedis(connection_pool=REDIS_POOL)
    return client.sismember(ADVERT_INFO_KEY, advert_info) == 1


def add_info(advert_info: List[str]) -> None:
    """Add the advert info hash to the cache"""
    client = redis.StrictRedis(connection_pool=REDIS_POOL)
    client.sadd(ADVERT_INFO_KEY, *advert_info)
