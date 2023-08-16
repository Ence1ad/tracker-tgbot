

import redis

with redis.Redis(host='localhost', port=6379, decode_responses=True) as r:
    r.hset(name='my_dict', key='name', value="Co company")
    r.hset(name='my_dict', key='age', value="1980")
    r.hset(name='my_dict', key='revenue', value="100")

    r.expire('my_dict', time=10)

    print(r.hgetall('my_dict'))



