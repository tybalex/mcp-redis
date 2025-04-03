from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp


@mcp.tool()
async def set_redis_string(key: str, value: str, expiration: int = None) -> str:
    """Set a Redis string value with an optional expiration time.

    Args:
        key (str): The key to set.
        value (str): The value to store.
        expiration (int, optional): Expiration time in seconds.

    Returns:
        str: Confirmation message or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        if expiration:
            r.setex(key, expiration, value)
        else:
            r.set(key, value)
        return f"Successfully set {key}" + (f" with expiration {expiration} seconds" if expiration else "")
    except RedisError as e:
        return f"Error setting key {key}: {str(e)}"


@mcp.tool()
async def get_redis_string(key: str) -> str:
    """Get a Redis string value.

    Args:
        key (str): The key to retrieve.

    Returns:
        str: The stored value or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        value = r.get(key)
        return value if value else f"Key {key} does not exist"
    except RedisError as e:
        return f"Error retrieving key {key}: {str(e)}"


@mcp.tool()
async def delete_redis_key(key: str) -> str:
    """Delete a Redis key.

    Args:
        key (str): The key to delete.

    Returns:
        str: Confirmation message or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        result = r.delete(key)
        return f"Successfully deleted {key}" if result else f"Key {key} not found"
    except RedisError as e:
        return f"Error deleting key {key}: {str(e)}"
