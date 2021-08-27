#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

"""
由于使用了django，而它自带的ORM不好用，学习成本太高，因此，自己写了一个，从网上的数据库连接池修改。
"""
class BasePymysql(object):
    def __init__(self):
        self.db_host = 'localhost'
        self.db_port = int('3306')
        self.user = 'root'
        self.password = str('123456')
        self.db = 'remvocabulary_dbms'
        self.conn = None
        self.cursor = None


class MyPymysql(BasePymysql):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用单次连接，实现获取连接对象
    """
    # 连接池对象（暂时不需要）
    __pool = None

    def __init__(self, usePool=False):
        super(MyPymysql, self).__init__()
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self.usePool = usePool
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if self.usePool:
            if MyPymysql.__pool is None:
                __pool = PooledDB(creator=pymysql,
                                  mincached=1,
                                  maxcached=20,
                                  host=self.db_host,
                                  port=self.db_port,
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.db,
                                  use_unicode=False,
                                  charset="utf8",
                                  cursorclass=DictCursor)
            return __pool.connection()
        else:
            conn = pymysql.connect(host=self.db_host, user=self.user, password=self.password, database=self.db, autocommit=True)
            return conn

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.autocommit(1)

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()


# if __name__ == '__main__':
#     mysql = MyPymysqlPool()
#
#     sqlAll = "select * from myTest.aa;"
#     result = mysql.getAll(sqlAll)
#     print(result)
#
#     sqlAll = "select * from myTest.aa;"
#     result = mysql.getMany(sqlAll, 2)
#     print(result)
#
#     result = mysql.getOne(sqlAll)
#     print(result)
#
#     # mysql.insert("insert into myTest.aa set a=%s", (1))
#
#     # 释放资源
#     mysql.dispose()
