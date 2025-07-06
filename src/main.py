import sys
import os
import urllib.parse
import click

from src.common.connection import RedisConnectionManager
from src.common.server import mcp
import src.tools.server_management
import src.tools.misc
import src.tools.redis_query_engine
import src.tools.hash
import src.tools.list
import src.tools.string
import src.tools.json
import src.tools.sorted_set
import src.tools.set
import src.tools.stream
import src.tools.pub_sub
from src.common.config import MCP_TRANSPORT


class RedisMCPServer:
    def __init__(self):
        print("Starting the Redis MCP Server", file=sys.stderr)

    def run(self):
        mcp.run(transport=MCP_TRANSPORT)

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


@click.command()
@click.option('--url', help='Redis connection URI (redis://user:pass@host:port/db or rediss:// for SSL)')
@click.option('--host', default='127.0.0.1', help='Redis host')
@click.option('--port', default=6379, type=int, help='Redis port')
@click.option('--db', default=0, type=int, help='Redis database number')
@click.option('--username', help='Redis username')
@click.option('--password', help='Redis password')
@click.option('--ssl', is_flag=True, help='Use SSL connection')
@click.option('--ssl-ca-path', help='Path to CA certificate file')
@click.option('--ssl-keyfile', help='Path to SSL key file')
@click.option('--ssl-certfile', help='Path to SSL certificate file')
@click.option('--ssl-cert-reqs', default='required', help='SSL certificate requirements')
@click.option('--ssl-ca-certs', help='Path to CA certificates file')
@click.option('--cluster-mode', is_flag=True, help='Enable Redis cluster mode')
@click.option('--mcp-transport', default='stdio', type=click.Choice(['stdio', 'streamable-http', 'sse']), help='MCP transport method')
@click.option('--mcp-host', default='127.0.0.1', help='MCP server host (for http/sse transport)')
@click.option('--mcp-port', default=8000, type=int, help='MCP server port (for http/sse transport)')
def cli(url, host, port, db, username, password,
        ssl, ssl_ca_path, ssl_keyfile, ssl_certfile,
        ssl_cert_reqs, ssl_ca_certs, cluster_mode,
        mcp_transport, mcp_host, mcp_port):
    """Redis MCP Server - Model Context Protocol server for Redis."""

    # Handle Redis URI if provided
    if url:
        try:
            uri_config = parse_redis_uri(url)
            set_redis_env_from_config(uri_config)
        except ValueError as e:
            click.echo(f"Error parsing Redis URI: {e}", err=True)
            sys.exit(1)
    else:
        # Set individual Redis parameters
        config = {
            'host': host,
            'port': port,
            'db': db,
            'ssl': ssl,
            'cluster_mode': cluster_mode
        }

        if username:
            config['username'] = username
        if password:
            config['password'] = password
        if ssl_ca_path:
            config['ssl_ca_path'] = ssl_ca_path
        if ssl_keyfile:
            config['ssl_keyfile'] = ssl_keyfile
        if ssl_certfile:
            config['ssl_certfile'] = ssl_certfile
        if ssl_cert_reqs:
            config['ssl_cert_reqs'] = ssl_cert_reqs
        if ssl_ca_certs:
            config['ssl_ca_certs'] = ssl_ca_certs

        set_redis_env_from_config(config)

    # Set MCP transport settings
    os.environ['MCP_TRANSPORT'] = mcp_transport
    os.environ['MCP_HOST'] = mcp_host
    os.environ['MCP_PORT'] = str(mcp_port)

    # Start the server
    server = RedisMCPServer()
    server.run()


def main():
    """Legacy main function for backward compatibility."""
    server = RedisMCPServer()
    server.run()


if __name__ == "__main__":
    main()
