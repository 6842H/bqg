# coding: utf-8

from traceback import format_exc
import pymysql
from DBUtils.PooledDB import PooledDB
from threading import Timer
from config import DB


class DBPool:
    __pool = None

    @staticmethod
    def show_pool():
        if DBPool.__pool:
            print('数据库连接池状态：')
            print('当前连接数：', DBPool.__pool._connections, '允许最大连接数', DBPool.__pool._maxconnections)
        else:
            print('初始化连接池')
            DBPool.__pool = DBPool.__get_pool()
        Timer(10, DBPool.show_pool).start()

    def __init__(self):
        con = DBPool.__get_pool()
        cursor = con.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        if cursor:
            cursor.close()
        if con:
            con.close()
        print('database version: %s' % version)
        pass

    @staticmethod
    def __get_pool():
        if not DBPool.__pool:
            # DBPool.__pool = PooledDB(pymysql, 10, host='localhost', user='root', passwd='123', db='ex71', port=3306, charset='utf8', blocking=True, setsession=['SET AUTOCOMMIT = 1'])
            DBPool.__pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=DB.maxconnections,  # 连接池允许的最大连接数，0和None表示没有限制
                mincached=DB.mincached,  # 初始化时，连接池至少创建的空闲的连接，0表示不创建
                maxcached=DB.maxcached,  # 连接池空闲的最多连接数，0和None表示没有限制
                maxshared=3,
                # 连接池中最多共享的连接数量，0和None表示全部共享，ps:其实并没有什么用，因为pymsql和MySQLDB等模块中的threadsafety都为1，所有值无论设置多少，_maxcahed永远为0，所以永远是所有链接共享
                blocking=True,  # 链接池中如果没有可用共享连接后，是否阻塞等待，True表示等待，False表示不等待然后报错
                setsession=[],  # 开始会话前执行的命令列表
                ping=0,  # ping Mysql 服务端，检查服务是否可用
                host=DB.host,
                port=DB.port,
                user=DB.user,
                password=DB.password,
                database=DB.database,
                charset='utf8'
            )
        return DBPool.__pool.connection()

    # 插入一条数据，table_name：表名、cols_list：列名，values_list：值列表(一维)
    # 修改成元组后兼容插入多条数据
    # 若只插入一条数据，传入tuple， 插入多条传入列表
    @staticmethod
    def insert_item(table_name, cols_tuple, values_tuple):
        if isinstance(values_tuple, list):
            values_tuple = ','.join([str(tuple(i)).replace(',)', ')') for i in values_tuple])
        else:
            values_tuple = str(values_tuple)
        sql = """insert into `%s`(`%s`) values%s""" % (table_name, "`,`".join(cols_tuple), values_tuple)
        # print(sql)
        con = DBPool.__get_pool()
        if not con:
            print('未获取到con')
            return
        cursor = con.cursor()
        try:
            cursor.execute(sql)
            con.commit()
            # cursor.close()      # 归还到连接池
            # con.close()
        except Exception as e:
            try:
                con.rollback()
            except Exception as ee:
                # print('insert_item rollback error>>>>', ee)
                print(format_exc(), ee)
            print(format_exc(), e)
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
        pass

    # 传入字典mdict，字段table: 表名，key：列名，values：值（二维）
    @staticmethod
    def insert_item_by_dict(mdict):
        # print('mdict', mdict)
        if mdict:
            # print(mdict['table'], mdict['cols'], mdict['values'])
            DBPool.insert_item(mdict['table'], mdict['cols'], mdict['values'])


    # 执行sql
    @staticmethod
    def exe_sql(sql):
        # print(sql)
        con = DBPool.__get_pool()
        if not con:
            print('未获取到con')
            return
        cursor = con.cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            con.commit()
            return res
        except Exception as e:
            try:
                con.rollback()
            except Exception as ee:
                # print('exe_sql rollback error>>>>', ee)
                print(format_exc(), ee)
            print(format_exc(), e)
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
        return None
        pass





'''
db = DBPool()
#db.insert_items('test', ['id', 'name'], [['222', '111']])
res = db.get_items(table='test',col_list=['name','id'],limit=2)
print(res)
'''
# DBPool().show_pool()

