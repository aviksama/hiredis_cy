#include <stdlib.h>

#include "hiredis/hiredis.h"

redisContext * getconnection(void);
redisReply* getreply(redisContext *c, const char *command);
