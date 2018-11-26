import sys
import gevent
from gevent.lock import BoundedSemaphore
import six
from cywrap import CommandError, ConnectionError, Connection, ConnectionLimitExceeded


class ConnectionPool(object):

    def __init__(self, max_connections=10, connection_class=Connection):
        self._max_connections = max_connections
        self._connection_class = connection_class
        self._reset()

    def _reset(self):
        self.available_connections = []
        self.lock = BoundedSemaphore()
        self.created_connections = 0

    # def _get_connection(self):
    #     try:
    #         with self.lock:
    #             connection = self.available_connections.pop()
    #             self.in_use_connections.add(connection)
    #     except IndexError:
    #         with self.lock:
    #             if self.created_connections < self._max_connections:
    #                 # new connections need to be created
    #                 connection = self._connection_class()
    #                 self.created_connections += 1
    #                 self.in_use_connections.add(connection)
    #             else:
    #                 raise ConnectionError("max connection limit exhausted, cannot create connection")
    #     return connection

    def _get_connection(self):
        with self.lock:
            if self.available_connections:
                connection = self.available_connections.pop()
            elif self.created_connections < self._max_connections:
                connection = self._connection_class()
                self.created_connections += 1
            else:
                raise ConnectionLimitExceeded("max connection limit exhausted, cannot create connection")
        return connection

    def _release(self, connection):
        with self.lock:
            self.available_connections.append(connection)

    def call(self, command):
        connection = None
        try:
            connection = self._get_connection()
            retval = connection.call(command)
            self._release(connection)
            return retval
        except ConnectionError:
                self._reset()
                connection = self._get_connection()
                try:
                    retval = connection.call(command)
                    self._release(connection)
                    return retval
                except CommandError as e:
                    self._release(connection)
                    six.reraise(CommandError, CommandError(e.args[0]), sys.exc_info()[2])
        except CommandError as e:
            self._release(connection)
            six.reraise(CommandError, CommandError(e.args[0]), sys.exc_info()[2])
