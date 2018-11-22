
cdef extern from "hiredis/hiredis.h":
    ctypedef struct redisReply:
        int type
        long long integer
        size_t len
        char *str
        size_t elements
        redisReply **element
    ctypedef struct redisContext:
        int err
        char errstr[128]
        pass
    void freeReplyObject(void *reply)
    void redisFree(redisContext *c)

cdef extern from "con.h":
    redisContext * getconnection()
    redisReply * getreply(redisContext *c, const char *command)