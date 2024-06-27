import functools
import logging

from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def cache(func):
    """
    Decorator for cache.
    If there is data in the cache, it takes it from there.
    If not, it receives the data (the decorated function) and saves it to the cache.
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        key = str(args) + '|' + str(kwargs)
        if data := await self.cache_service.retrieve_from_cache(key=key):
            logger.info('{}.{}: Retrieve data from cache'.format(type(self).__name__, func.__name__))
            return data
        if data := await func(self, *args, **kwargs):
            logger.info('{}.{}: Get data from Elasticsearch'.format(type(self).__name__, func.__name__))
            await self.cache_service.add_to_cache(key=key, data=data)
            logger.info('{}.{}: Save data to cache'.format(type(self).__name__, func.__name__))
            return data
        logger.warning('{}.{}: Item was not found in Elasticsearch'.format(type(self).__name__, func.__name__))
        return None

    return wrapper
