import sys
from version import __version__
import redis
from redis import Redis
from typing import Optional
from common.config import REDIS_CFG

class RedisConnectionManager:
    _instance: Optional[Redis] = None

    @classmethod
    def get_connection(cls, decode_responses=True) -> Redis:
        if cls._instance is None:
            try:
                print("Initializing Redis connection", file=sys.stderr)
                cls._instance = redis.StrictRedis(
                    host=REDIS_CFG["host"],
                    port=REDIS_CFG["port"],
                    password=REDIS_CFG["password"],
                    ssl=REDIS_CFG["ssl"],
                    ssl_ca_path=REDIS_CFG["ssl_ca_path"],
                    decode_responses=decode_responses,
                    max_connections=10,
                    lib_name=f"redis-py(mcp-server_v{__version__})"
                )

            except redis.exceptions.ConnectionError:
                print("Failed to connect to Redis server", file=sys.stderr)
                raise
            except redis.exceptions.AuthenticationError:
                print("Authentication failed", file=sys.stderr)
                raise
            except redis.exceptions.TimeoutError:
                print("Connection timed out", file=sys.stderr)
                raise
            except redis.exceptions.ResponseError as e:
                print(f"Response error: {e}", file=sys.stderr)
                raise
            except redis.exceptions.RedisError as e:
                print(f"Redis error: {e}", file=sys.stderr)
                raise
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr)
                raise

        return cls._instance
