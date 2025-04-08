from typing import Dict, Any
from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp


@mcp.tool()
async def execute_raw_command(command: str, *args) -> str:
    """Execute a raw Redis raw command like SET, GET, HSET, HGET, JSON.SET, JSON.GET, FT.SEARCH or FT.AGGREGATE.
       Every Redis command can be executed using this call

    Args:
        command (str): The Redis command to execute.
        *args: Additional arguments for the command.

    Returns:
        str: The result of the command execution or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        return r.execute_command(command, *args)
    except RedisError as e:
        return f"Error executing command {command}: {str(e)}"

@mcp.tool()  
async def get_key_info(key: str) -> Dict[str, Any]:
    try:
        r = RedisConnectionManager.get_connection()
        key_type = r.type(key).decode('utf-8')
        info = {
            'key': key,
            'type': key_type,
            'ttl': r.ttl(key)
        }

        if key_type == 'string':
            info['value'] = r.get(key)
        elif key_type == 'list':
            info['value'] = r.lrange(key, 0, -1)
        elif key_type == 'hash':
            info['value'] = r.hgetall(key)
        elif key_type == 'set':
            info['value'] = r.smembers(key)
        elif key_type == 'zset':
            info['value'] = r.zrange(key, 0, -1, withscores=True)
        elif key_type == 'ReJSON-RL':
            info['value'] = r.json().get(key, "$")
        
        return info
    except RedisError as e:
        return {'error': str(e)}