############# example code for performance comparison #############
import time

import gevent
import redis
from cyredis import ConnectionPool


def mycalldef(command):
    con = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")
    func_list = []
    for i in range(2000):
        func_list.append(gevent.spawn(con.hgetall, command))
    t = time.time()
    gevent.joinall(func_list)
    return time.time() - t


def mycall(command, pool=None):
    con = pool or ConnectionPool()
    func_list = []
    for i in range(2000):
        func_list.append(gevent.spawn(con.call, "hgetall %s" % command))
    t = time.time()
    gevent.joinall(func_list)
    return time.time() - t
