import json
from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp
from redis.commands.search.query import Query
from redis.commands.search.field import VectorField
from redis.commands.search.index_definition import IndexDefinition
import numpy as np


@mcp.tool() 
async def get_indexes() -> str:
    """List of indexes in the Redis database

    Returns:
        str: A JSON string containing the list of indexes or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        return json.dumps(r.execute_command("FT._LIST"))
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


@mcp.tool()
async def create_vector_index_hash(index_name: str = "vector_index",
                       prefix: str = "doc:",
                       vector_field: str = "vector",
                       dim: int = 1536,
                       distance_metric: str = "COSINE") -> str:
    """
    Create a Redis 8 vector similarity index using HNSW on a Redis hash.

    This function sets up a Redis index for approximate nearest neighbor (ANN)
    search using the HNSW algorithm and float32 vector embeddings.

    Args:
        index_name: The name of the Redis index to create. Unless specifically required, use the default name for the index.
        prefix: The key prefix used to identify documents to index (e.g., 'doc:'). Unless specifically required, use the default prefix.
        vector_field: The name of the vector field to be indexed for similarity search. Unless specifically required, use the default field name
        dim: The dimensionality of the vectors stored under the vector_field.
        distance_metric: The distance function to use (e.g., 'COSINE', 'L2', 'IP').

    Returns:
        A string indicating whether the index was created successfully or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()

        index_def = IndexDefinition(prefix=[prefix])
        schema = (
            VectorField(
                vector_field,
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": dim,
                    "DISTANCE_METRIC": distance_metric
                }
            )
        )

        r.ft(index_name).create_index([schema], definition=index_def)
        return f"Index '{index_name}' created successfully."
    except RedisError as e:
        return f"Error creating index '{index_name}': {str(e)}"


@mcp.tool()
async def vector_search_hash(query_vector: list,
                            index_name: str = "vector_index",
                            vector_field: str = "vector",
                            k: int = 5,
                            return_fields: list = None) -> list:
    """
    Perform a KNN vector similarity search using Redis 8 or later version on vectors stored in hash data structures.

    Args:
        query_vector: List of floats to use as the query vector.
        index_name: Name of the Redis index. Unless specifically specified, use the default index name.
        vector_field: Name of the indexed vector field. Unless specifically required, use the default field name
        k: Number of nearest neighbors to return.
        return_fields: List of fields to return (optional).

    Returns:
        A list of matched documents or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()

        # Convert query vector to float32 binary blob
        vector_blob = np.array(query_vector, dtype=np.float32).tobytes()

        # Build the KNN query
        base_query = f"*=>[KNN {k} @{vector_field} $vec_param AS score]"
        query = Query(base_query).sort_by("score").paging(0, k).return_fields("id", "score", *return_fields or []).dialect(2)

        # Perform the search with vector parameter
        results = r.ft(index_name).search(query, query_params={"vec_param": vector_blob})

        # Format and return the results
        return [doc.__dict__ for doc in results.docs]
    except RedisError as e:
        return f"Error performing vector search on index '{index_name}': {str(e)}"


@mcp.tool()
async def get_all_keys(pattern: str = "*") -> list:
    """
    Retrieve all keys matching a pattern from the Redis database using the KEYS command.
    
    Note: The KEYS command is blocking and can impact performance on large databases.
    For production use with large datasets, consider using SCAN instead.

    Args:
        pattern: Pattern to match keys against (default is "*" for all keys).
                Common patterns: "user:*", "cache:*", "*:123", etc.

    Returns:
        A list of keys matching the pattern or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        keys = r.keys(pattern)
        # Convert bytes to strings if needed
        return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
    except RedisError as e:
        return f"Error retrieving keys with pattern '{pattern}': {str(e)}"


@mcp.tool()
async def scan_keys(pattern: str = "*", count: int = 100, cursor: int = 0) -> dict:
    """
    Scan keys in the Redis database using the SCAN command (non-blocking, production-safe).
    
    The SCAN command iterates through the keyspace in small chunks, making it safe to use
    on large databases without blocking other operations.

    Args:
        pattern: Pattern to match keys against (default is "*" for all keys).
                Common patterns: "user:*", "cache:*", "*:123", etc.
        count: Hint for the number of keys to return per iteration (default 100).
               Redis may return more or fewer keys than this hint.
        cursor: The cursor position to start scanning from (0 to start from beginning).

    Returns:
        A dictionary containing:
        - 'cursor': Next cursor position (0 means scan is complete)
        - 'keys': List of keys found in this iteration
        - 'total_scanned': Number of keys returned in this batch
        Or an error message if something goes wrong.
    """
    try:
        r = RedisConnectionManager.get_connection()
        cursor, keys = r.scan(cursor=cursor, match=pattern, count=count)
        
        # Convert bytes to strings if needed
        decoded_keys = [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        
        return {
            'cursor': cursor,
            'keys': decoded_keys,
            'total_scanned': len(decoded_keys),
            'scan_complete': cursor == 0
        }
    except RedisError as e:
        return f"Error scanning keys with pattern '{pattern}': {str(e)}"


@mcp.tool()
async def scan_all_keys(pattern: str = "*", batch_size: int = 100) -> list:
    """
    Scan and return ALL keys matching a pattern using multiple SCAN iterations.
    
    This function automatically handles the SCAN cursor iteration to collect all matching keys.
    It's safer than KEYS * for large databases but will still collect all results in memory.

    Args:
        pattern: Pattern to match keys against (default is "*" for all keys).
        batch_size: Number of keys to scan per iteration (default 100).

    Returns:
        A list of all keys matching the pattern or an error message.
    """
    try:
        r = RedisConnectionManager.get_connection()
        all_keys = []
        cursor = 0
        
        while True:
            cursor, keys = r.scan(cursor=cursor, match=pattern, count=batch_size)
            
            # Convert bytes to strings if needed and add to results
            decoded_keys = [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
            all_keys.extend(decoded_keys)
            
            # Break when scan is complete (cursor returns to 0)
            if cursor == 0:
                break
        
        return all_keys
    except RedisError as e:
        return f"Error scanning all keys with pattern '{pattern}': {str(e)}"
