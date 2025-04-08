# Redis MCP Server

## Overview
The Redis MCP Server is a **natural language interface** designed for agentic applications to efficiently manage and search data in Redis. It integrates seamlessly with **MCP (Model Content Protocol) clients**, enabling AI-driven workflows to interact with structured and unstructured data in Redis.

## Features
- **Natural Language Queries**: Enables AI agents to query and update Redis using natural language.
- **Seamless MCP Integration**: Works with any **MCP client** for smooth communication.
- **Full Redis Support**: Handles **hashes, lists, sets, sorted sets, streams**, and more.
- **Search & Filtering**: Supports efficient data retrieval and searching in Redis.
- **Scalable & Lightweight**: Designed for **high-performance** data operations.

## Installation
```sh
# Clone the repository
git clone https://github.com/redis/mcp-redis.git
cd mcp-redis

# Install dependencies using uv
uv venv
source .venv/bin/activate
uv sync
```


## Configuration

To configure the Redis Cloud API MCP Server, consider the following environment variables:

| Name                    | Description                                               | Default Value |
|-------------------------|-----------------------------------------------------------|---------------|
| `REDIS_HOST`            | Redis IP or hostname                                      | `"127.0.0.1"` |
| `REDIS_PORT`            | Redis port                                                | `6379`        |
| `REDIS_USERNAME`        | Default database username                                 | `"default"`   |
| `REDIS_PWD`             | Default database password                                 | ""            |
| `REDIS_SSL`             | Enables or disables SSL/TLS                               | `False`       |
| `REDIS_CA_PATH`         | CA certificate for verifying server                       | None          |
| `REDIS_SSL_KEYFILE`     | Client's private key file for client authentication       | None          |
| `REDIS_SSL_CERTFILE`    | Client's certificate file for client authentication       | None          |
| `REDIS_CERT_REQS`       | Whether the client should verify the server's certificate | `"required"`  |
| `REDIS_CA_CERTS`        | Path to the trusted CA certificates file                  | None          |

## Integration with Claude Desktop
You can configure Claude Desktop to use this MCP Server.

1. Specify your Redis credentials and TLS configuration
2. Retrieve your `uv` command full path (e.g. `which uv`)
3. Edit the `claude_desktop_config.json` configuration file 
   - on a MacOS, at `~/Library/Application\ Support/Claude/`

```commandline
{
    "mcpServers": {
        "redis": {
            "command": "<full_path_uv_command>",
            "args": [
                "--directory",
                "<your_mcp_server_directory>",
                "run",
                "src/main.py"
            ],
            "env": {
                "REDIS_HOST": "<your_redis_database_hostname>",
                "REDIS_PORT": "<your_redis_database_port>",
                "REDIS_PSW": "<your_redis_database_password>",
                "REDIS_SSL": True|False,
                "REDIS_CA_PATH": "<your_redis_ca_path>"
            }
        }
    }
}
```

You can troubleshoot problems by tailing the log file.

```commandline
tail -f ~/Library/Logs/Claude/mcp-server-redis.log
```

## Testing

You can use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) for visual debugging of this MCP Server.

```sh
npx @modelcontextprotocol/inspector uv run src/main.py
```

## Example Use Cases
- **AI Assistants**: Enable LLMs to fetch, store, and process data in Redis.
- **Chatbots & Virtual Agents**: Retrieve session data, manage queues, and personalize responses.
- **Data Search & Analytics**: Query Redis for **real-time insights and fast lookups**.
- **Event Processing**: Manage event streams with **Redis Streams**.

## Contributing
1. Fork the repo
2. Create a new branch (`feature-branch`)
3. Commit your changes
4. Push to your branch and submit a PR!

## License
This project is licensed under the **MIT License**.

## Contact
For questions or support, reach out via [GitHub Issues](https://github.com/redis/mcp-redis-server/issues).

