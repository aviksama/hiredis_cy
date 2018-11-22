import sys
import time

import gevent
from gevent.lock import BoundedSemaphore
from cymod import *
import redis
import six


class ConnectionPool(object):

    def __init__(self, max_connections=1, connection_class=Connection):
        self._max_connections = max_connections
        self._connection_class = connection_class
        self._reset()

    def _reset(self):
        self.lock = BoundedSemaphore()
        self.available_connections = []
        self.in_use_connections = set()
        self.created_connections = 0

    def _get_connection(self):
        with self.lock:
            if self.available_connections:
                connection = self.available_connections.pop()
                self.in_use_connections.add(connection)
            elif self.created_connections < self._max_connections:
                connection = self._connection_class()
                self.created_connections += 1
                self.in_use_connections.add(connection)
            else:
                raise ConnectionError("max connection limit exhausted, cannot create connection")
        return connection

    def _release(self, connection):
        if not isinstance(connection, self._connection_class):
            return
        with self.lock:
            try:
                self.in_use_connections.remove(connection)
                self.available_connections.append(connection)
            except KeyError:
                pass

    def call(self, command):
        connection = None
        try:
            connection = self._get_connection()
            retval = connection.call(command)
            self._release(connection)
            return retval
        except ConnectionError as e:
            if self.created_connections > 0:
                self._reset()
                connection = self._get_connection()
                retval = connection.call(command)
                return retval
            else:
                six.reraise(ConnectionError, ConnectionError(e.args[0]), sys.exc_info()[2])
        except CommandError as e:
            self._release(connection)
            six.reraise(CommandError, CommandError(e.args[0]), sys.exc_info()[2])


# def mycalldef(command):
#     con = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")
#     for i in range(200):
#         con.hgetall(command)
#
# def mycall(command):
#     con = ConnectionPool()
#     for i in range(200):
#         con.call("hgetall " + command)
#
# def fun(func, command):
#     li = []
#     for i in range(100):
#         li.append(gevent.spawn(func, command))
#     t = time.time()
#     gevent.joinall(li)
#     return time.time() - t