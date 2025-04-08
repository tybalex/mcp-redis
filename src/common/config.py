from dotenv import load_dotenv
import os

load_dotenv()

REDIS_CFG = {"host": os.getenv('REDIS_HOST', '127.0.0.1'),
             "port": int(os.getenv('REDIS_PORT',6379)),
             "username": os.getenv('REDIS_USERNAME','default'),
             "password": os.getenv('REDIS_PWD',''),
             "ssl": os.getenv('REDIS_SSL', False),
             "ssl_ca_path": os.getenv('REDIS_CA_PATH',''),
             "ssl_keyfile": os.getenv('REDIS_SSL_KEYFILE', ''),
             "ssl_certfile": os.getenv('REDIS_SSL_CERTFILE', ''),
             "ssl_cert_reqs": os.getenv('REDIS_CERT_REQS', ''),
             "ssl_ca_certs": os.getenv('REDIS_CA_CERTS', '')}