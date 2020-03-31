import os
import redis
from redis import Redis
from rq import Worker, Queue, Connection

#CHANNEL_LAYERS = {
    #"default": {
        # This example app uses the Redis channel layer implementation asgi_redis
        #"BACKEND": "asgi_redis.RedisChannelLayer",
        #"CONFIG": {
            #"hosts": [(redis_host, 8050)],
        #},
        #"ROUTING": "multichat.routing.channel_routing",
    #},
#}

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL')
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
