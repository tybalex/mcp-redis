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