# coding:utf-8


class DB:
    maxconnections = 10  # 连接池允许的最大连接数，0和None表示没有限制
    mincached = 0  # 初始化时，连接池至少创建的空闲的连接，0表示不创建
    maxcached = 0  # 连接池空闲的最多连接数，0和None表示没有限制
    host = '127.0.0.1'
    port = 3306
    user = 'bqger'
    password = 'bqg123'
    database = 'bqg'

