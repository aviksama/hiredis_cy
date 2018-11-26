cimport cimp
from libc.stdlib cimport free, malloc

#define REDIS_REPLY_STRING 1
#define REDIS_REPLY_ARRAY 2
#define REDIS_REPLY_INTEGER 3
#define REDIS_REPLY_NIL 4
#define REDIS_REPLY_STATUS 5
#define REDIS_REPLY_ERROR 6

class ConnectionError(Exception):
    pass
class CommandError(Exception):
    pass
class ConnectionLimitExceeded(Exception):
    pass


cdef parse_reply(cimp.redisReply *reply, const int is_parent):
    cdef cimp.redisReply **sub_reply = <cimp.redisReply **>malloc(sizeof(cimp.redisReply));
    reptype = <int>reply.type
    if reptype in (1, 5):
        rval = <bytes> reply.str
    elif reptype == 3:
        rval = <long long> reply.integer
    elif reptype == 4:
        rval = None
    elif reptype == 6:
        rval = <bytes> reply.str
        raise CommandError(rval.decode("utf-8"))
    else: # 2
        array = []
        number_of_elements = <int> reply.elements
        if number_of_elements <= 0:
            cimp.freeReplyObject(reply)
            free(sub_reply)
            return array
        sub_reply = <cimp.redisReply **>reply.element
        for i in range(number_of_elements):
            python_reply = parse_reply(sub_reply[i], 0)
            array.append(python_reply)
        free(sub_reply)
        return array
    cimp.freeReplyObject(reply)
    free(sub_reply)
    return rval


cdef class Connection(object):
    __slots__ = ["connection", "replyobj", "is_destroyed"]
    cdef cimp.redisContext * connection
    cdef cimp.redisReply *replyobj
    cdef int is_destroyed

    def __cinit__(self):
        self.connection = cimp.getconnection()
        if self.connection == NULL:
            raise  ConnectionError("out of memory")
        if self.connection[0].err== 1:
            e_str = <bytes> self.connection[0].errstr
            raise ConnectionError(e_str)
        self.is_destroyed = 0
        self.replyobj = NULL

    def __dealloc__(self):
        self._destroy()

    def call(self, command):
        if self.is_destroyed:
            raise ConnectionError("could not connect to the server, when tried executing command")
        command = command.encode('utf-8')
        self.replyobj = cimp.getreply(self.connection, command)
        if self.replyobj == NULL:
            cimp.freeReplyObject(self.replyobj)
            raise ConnectionError("could not connect to the server, when tried executing command")
        retval = parse_reply(self.replyobj, 1)
        return retval

    def _destroy(self):
        if self.is_destroyed == 0:
            self.is_destroyed = 1
            cimp.redisFree(self.connection)
