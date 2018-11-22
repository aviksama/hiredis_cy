#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hiredis/hiredis.h"
#include "con.h"


redisContext * getconnection(){
    redisContext *c = (redisContext *) malloc(sizeof(redisContext));
    struct timeval timeout = { 1, 500000 };
    const char* sock = getenv("REDIS_PATH");
    if (sock == NULL){
    c = redisConnectUnixWithTimeout("/tmp/redis.sock", timeout);
    } else {
    c = redisConnectUnixWithTimeout(sock, timeout);
    }
    return c;
    }


redisReply * getreply(redisContext *c, const char *command){
    redisReply *reply = (redisReply *)malloc(sizeof(redisReply));
    reply = redisCommand(c, command);
    return reply;
}

