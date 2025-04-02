from common.connection import RedisConnectionManager
from common.server import mcp
import tools.server_management
import tools.misc 
import tools.redis_query_engine
import tools.hash  

class RedisMCPServer:
    def __init__(self):
        redis_client = RedisConnectionManager.get_connection()
        print(redis_client.ping())

    def run(self):
        mcp.run(transport='stdio')

if __name__ == "__main__":
    server = RedisMCPServer()
    server.run()
