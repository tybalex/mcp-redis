from typing import Dict, Any
from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp


@mcp.tool() 
async def get_indexes() -> str:
    """List of indexes in the Redis database
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.execute_command("FT._LIST")
    except RedisError as e:
        return f"Error retrieving indexes: {str(e)}"