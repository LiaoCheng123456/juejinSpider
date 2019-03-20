# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

# 检查Elastic
import time

import requests


from juejinspider.tools.ConnectionPool import redisConnectionPool

# 检查elasticsearch是否已启动
def es():
    try:
        requests.get("http://192.168.136.211:9200", timeout=3)
        return True
    except:
        time.sleep(1)
        print("es连接超时，正在重试...")
        es()

# 检查redis是否已经启动
def redisConnectTest():
    try:
        redis = redisConnectionPool()
        redis.getClient().ping()
    except:
        time.sleep(1)
        print("redis连接超时，正在重试...")
        redisConnectTest()
es()
redisConnectTest()