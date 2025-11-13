from config import RedisConfig
from redis import ConnectionPool, Redis


def new_redis_client(redis_config: RedisConfig) -> Redis:
    pool = ConnectionPool(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_config.password,
        max_connections=20,
    )
    return Redis(connection_pool=pool)
