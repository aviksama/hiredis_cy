# hiredis_cy
hiredis wrapper using cython for fast threadsafe redis access in python.

**installation**
* Install using python-pip.
* Requires python 3.6

        pip install git+https://github.com/aviksama/hiredis_cy.git

**using the application**
* currently it supports redis connection using unix socket only
* set the socket path by setting the environment variable `$REDIS_PATH`
* default path for redis sock file is `/tmp/redis.sock`
* example code for using the connection
        
      >>> from cyredis import ConnectionPool
      >>> pool = ConnectionPool(max_connections=50)
      >>> pool.call("PING")
      b'PONG'
      >>>
      