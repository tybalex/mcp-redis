import sys
from version import __version__
import redis
from redis import Redis
from redis.cluster import RedisCluster
from typing import Optional, Union, List, Dict, Any, Tuple
from common.config import REDIS_CFG, REDIS_CLUSTER_MODE, REDIS_CLUSTER_NODES

from common.config import generate_redis_uri


class RedisConnectionManager:
    _instance: Optional[Union[Redis, RedisCluster]] = None

    @classmethod
    def get_connection(cls, decode_responses=True) -> Union[Redis, RedisCluster]:
        if cls._instance is None:
            try:
                if REDIS_CLUSTER_MODE:
                    # In cluster mode, we can connect to one node and the client will discover the rest
                    # If specific cluster nodes are provided, use the first one as the startup node
                    if REDIS_CLUSTER_NODES and REDIS_CLUSTER_NODES[0]:
                        node = REDIS_CLUSTER_NODES[0]
                        if ':' in node:
                            host, port = node.split(':')
                            port = int(port)
                        else:
                            # Default to the configured port if only host is provided
                            host = node
                            port = REDIS_CFG["port"]
                    else:
                        # Use the primary node from REDIS_CFG as the startup node
                        host = REDIS_CFG["host"]
                        port = REDIS_CFG["port"]
                    
                    cls._instance = RedisCluster(
                        host=host,
                        port=port,
                        username=REDIS_CFG["username"],
                        password=REDIS_CFG["password"],
                        ssl=REDIS_CFG["ssl"],
                        ssl_ca_path=REDIS_CFG["ssl_ca_path"],
                        ssl_keyfile=REDIS_CFG["ssl_keyfile"],
                        ssl_certfile=REDIS_CFG["ssl_certfile"],
                        ssl_cert_reqs=REDIS_CFG["ssl_cert_reqs"],
                        ssl_ca_certs=REDIS_CFG["ssl_ca_certs"],
                        decode_responses=decode_responses,
                        max_connections_per_node=10,
                        lib_name=f"redis-py(mcp-server_v{__version__})"
                    )
                else:
                    cls._instance = redis.Redis(
                        host=REDIS_CFG["host"],
                        port=REDIS_CFG["port"],
                        username=REDIS_CFG["username"],
                        password=REDIS_CFG["password"],
                        ssl=REDIS_CFG["ssl"],
                        ssl_ca_path=REDIS_CFG["ssl_ca_path"],
                        ssl_keyfile=REDIS_CFG["ssl_keyfile"],
                        ssl_certfile=REDIS_CFG["ssl_certfile"],
                        ssl_cert_reqs=REDIS_CFG["ssl_cert_reqs"],
                        ssl_ca_certs=REDIS_CFG["ssl_ca_certs"],
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
            except redis.exceptions.ClusterError as e:
                print(f"Redis Cluster error: {e}", file=sys.stderr)
                raise
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr)
                raise

        return cls._instance
