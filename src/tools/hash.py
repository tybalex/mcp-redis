from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp

@mcp.tool()
async def hset(name: str, key: str, value: str) -> str:
    """Set a field in a hash stored at key.
    
    Args:
        name: The Redis hash key.
        key: The field name inside the hash.
        value: The value to set.
    
    Returns:
        A success message or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        r.hset(name, key, value)
        return f"Field '{key}' set successfully in hash '{name}'."
    except RedisError as e:
        return f"Error setting field '{key}' in hash '{name}': {str(e)}"

@mcp.tool()
async def hget(name: str, key: str) -> str:
    """Get the value of a field in a Redis hash.
    
    Args:
        name: The Redis hash key.
        key: The field name inside the hash.
    
    Returns:
        The field value or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        value = r.hget(name, key)
        return value.decode() if value else f"Field '{key}' not found in hash '{name}'."
    except RedisError as e:
        return f"Error getting field '{key}' from hash '{name}': {str(e)}"

@mcp.tool()
async def hdel(name: str, key: str) -> str:
    """Delete a field from a Redis hash.
    
    Args:
        name: The Redis hash key.
        key: The field name inside the hash.
    
    Returns:
        A success message or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        deleted = r.hdel(name, key)
        return f"Field '{key}' deleted from hash '{name}'." if deleted else f"Field '{key}' not found in hash '{name}'."
    except RedisError as e:
        return f"Error deleting field '{key}' from hash '{name}': {str(e)}"

@mcp.tool()
async def hgetall(name: str) -> dict:
    """Get all fields and values from a Redis hash.
    
    Args:
        name: The Redis hash key.
    
    Returns:
        A dictionary of field-value pairs or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        hash_data = r.hgetall(name)
        return {k: v for k, v in hash_data.items()} if hash_data else f"Hash '{name}' is empty or does not exist."
    except RedisError as e:
        return f"Error getting all fields from hash '{name}': {str(e)}"

@mcp.tool()
async def hexists(name: str, key: str) -> bool:
    """Check if a field exists in a Redis hash.
    
    Args:
        name: The Redis hash key.
        key: The field name inside the hash.
    
    Returns:
        True if the field exists, False otherwise.
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.hexists(name, key)
    except RedisError as e:
        return f"Error checking existence of field '{key}' in hash '{name}': {str(e)}"
