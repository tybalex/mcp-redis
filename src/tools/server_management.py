from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp

@mcp.tool()
async def get_dbsize() -> int:
    """Get the number of keys stored in the Redis database
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.dbsize()
    except RedisError as e:
        return f"Error getting database size: {str(e)}"