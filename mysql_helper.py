#! python3
# __author__ = "YangJiaHao"
# date: 2017/10/2
import pymysql


class MysqlHelper(object):
    def __init__(self, user, passwd, db, host='localhost', port=3306, charset='utf8'):
        """ initialize
        :param user: string
        :param passwd: string
        :param db: string
        :param host: string | None
        :param port: int | None
        :param charset: string | None
        """
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__charset = charset
        self.__db = db
        self.conn = None
        self.cursor = None

    def connect(self):
        # 链接数据库
        self.conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user, passwd=self.__passwd,
                                    charset=self.__charset, db=self.__db)
        self.cursor = self.conn.cursor()

    def close(self):
        # 关闭数据库
        self.cursor.close()
        self.conn.close()

    def process(self, sql, params=()):
        """执行sql命令，通用，自动连接，关闭。
        :param sql: string
        :param params: tuple | None
        :return: None
        """
        try:
            self.connect()
            self.cursor.execute(sql, params)
            self.conn.commit()
            self.close()
        except Exception as er:
            print('execute error:', er)

    def search(self, sql, params=()):
        """数据库查询，手动连接，关闭
        :param sql: string
        :param params: tuple | None
        :return: tuple
        """
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            self.close()
            return result
        except Exception as er:
            print('search error:', er)

    def insert(self, sql, params=()):
        """ 插入数据，手动连接，关闭。
        :param sql: string
        :param params: tuple | None
        :return: None
        """
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
        except Exception as er:
            print('insert error:', er)


if __name__ == '__main__':
    helper = MysqlHelper(user='root', passwd='225669', host='10.17.98.72', db='python3')
    sql = 'select * from goods'
    result = helper.search(sql)
    print(result)
