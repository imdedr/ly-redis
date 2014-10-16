import lyredis

redis = lyredis.lyredis("107.167.182.189", auth="ohfoundpass")
print redis.set("a", "Keniver")
print redis.get("a")
print redis.lpush("test", "a")
print redis.blpop("test", 0)
redis.close()