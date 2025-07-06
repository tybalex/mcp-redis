from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

MCP_TRANSPORT = os.getenv('MCP_TRANSPORT', 'stdio')
MCP_HOST = os.getenv('MCP_HOST', '127.0.0.1')
MCP_PORT = os.getenv('MCP_PORT', 8000)

def _load_redis_config():
    """Load Redis configuration from environment variables."""
    return {"host": os.getenv('REDIS_HOST', '127.0.0.1'),
            "port": int(os.getenv('REDIS_PORT',6379)),
            "username": os.getenv('REDIS_USERNAME', None),
            "password": os.getenv('REDIS_PWD',''),
            "ssl": os.getenv('REDIS_SSL', False) in ('true', '1', 't'),
            "ssl_ca_path": os.getenv('REDIS_SSL_CA_PATH', None),
            "ssl_keyfile": os.getenv('REDIS_SSL_KEYFILE', None),
            "ssl_certfile": os.getenv('REDIS_SSL_CERTFILE', None),
            "ssl_cert_reqs": os.getenv('REDIS_SSL_CERT_REQS', 'required'),
            "ssl_ca_certs": os.getenv('REDIS_SSL_CA_CERTS', None),
            "cluster_mode": os.getenv('REDIS_CLUSTER_MODE', False) in ('true', '1', 't'),
            "db": int(os.getenv('REDIS_DB', 0))}

REDIS_CFG = _load_redis_config()


def reload_redis_config():
    """Reload Redis configuration from environment variables."""
    global REDIS_CFG
    REDIS_CFG = _load_redis_config()


def parse_redis_uri(uri: str) -> dict:
    """Parse a Redis URI and return connection parameters."""
    parsed = urllib.parse.urlparse(uri)

    config = {}

    # Scheme determines SSL
    if parsed.scheme == 'rediss':
        config['ssl'] = True
    elif parsed.scheme == 'redis':
        config['ssl'] = False
    else:
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    # Host and port
    config['host'] = parsed.hostname or '127.0.0.1'
    config['port'] = parsed.port or 6379

    # Database
    if parsed.path and parsed.path != '/':
        try:
            config['db'] = int(parsed.path.lstrip('/'))
        except ValueError:
            config['db'] = 0
    else:
        config['db'] = 0

    # Authentication
    if parsed.username:
        config['username'] = parsed.username
    if parsed.password:
        config['password'] = parsed.password

    # Parse query parameters for SSL and other options
    if parsed.query:
        query_params = urllib.parse.parse_qs(parsed.query)

        # Handle SSL parameters
        if 'ssl_cert_reqs' in query_params:
            config['ssl_cert_reqs'] = query_params['ssl_cert_reqs'][0]
        if 'ssl_ca_certs' in query_params:
            config['ssl_ca_certs'] = query_params['ssl_ca_certs'][0]
        if 'ssl_ca_path' in query_params:
            config['ssl_ca_path'] = query_params['ssl_ca_path'][0]
        if 'ssl_keyfile' in query_params:
            config['ssl_keyfile'] = query_params['ssl_keyfile'][0]
        if 'ssl_certfile' in query_params:
            config['ssl_certfile'] = query_params['ssl_certfile'][0]

        # Handle other parameters
        if 'db' in query_params:
            try:
                config['db'] = int(query_params['db'][0])
            except ValueError:
                pass

    return config


def set_redis_env_from_config(config: dict):
    """Set environment variables from Redis configuration."""
    env_mapping = {
        'host': 'REDIS_HOST',
        'port': 'REDIS_PORT',
        'db': 'REDIS_DB',
        'username': 'REDIS_USERNAME',
        'password': 'REDIS_PWD',
        'ssl': 'REDIS_SSL',
        'ssl_ca_path': 'REDIS_SSL_CA_PATH',
        'ssl_keyfile': 'REDIS_SSL_KEYFILE',
        'ssl_certfile': 'REDIS_SSL_CERTFILE',
        'ssl_cert_reqs': 'REDIS_SSL_CERT_REQS',
        'ssl_ca_certs': 'REDIS_SSL_CA_CERTS',
        'cluster_mode': 'REDIS_CLUSTER_MODE'
    }

    for key, env_var in env_mapping.items():
        if key in config:
            value = config[key]
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            os.environ[env_var] = str(value)
            print(f"Setting {env_var} to {value}")
