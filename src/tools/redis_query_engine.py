from typing import Dict, Any
from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp
from redis.commands.search.query import Query


@mcp.tool() 
async def get_indexes() -> str:
    """List of indexes in the Redis database
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.execute_command("FT._LIST")
    except RedisError as e:
        return f"Error retrieving indexes: {str(e)}"


@mcp.tool()
async def get_index_info(index_name: str) -> str:
    """Retrieve schema and information about a specific Redis index using FT.INFO.

    Args:
        index_name (str): The name of the index to retrieve information about.

    Returns:
        str: Information about the specified index or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.ft(index_name).info()
    except RedisError as e:
        return f"Error retrieving index info: {str(e)}"


@mcp.tool()
async def get_indexed_keys_number(index_name: str) -> str:
    """Retrieve the number of indexed keys by the index

    Args:
        index_name (str): The name of the index to retrieve information about.

    Returns:
        int: Number of indexed keys
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.ft(index_name).search(Query("*")).total
    except RedisError as e:
        return f"Error retrieving number of keys: {str(e)}"

