from typing import Dict, Any
from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp


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
        
        return info
    except RedisError as e:
        return {'error': str(e)}