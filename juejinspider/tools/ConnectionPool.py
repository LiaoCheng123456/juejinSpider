import time

import redis
import requests


class redisConnectionPool:
    def __init__(self):
        self.pool = redis.ConnectionPool(host="192.168.136.211", port=6379, password=123456, socket_connect_timeout=2)

    def getClient(self):
        r = redis.Redis(connection_pool=self.pool)
        return r
