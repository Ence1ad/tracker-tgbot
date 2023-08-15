import redis

with redis.Redis(host='localhost', port=6379, decode_responses=True) as r:
    r.set('foo', 'bar')
    print(r.get('foo'))
