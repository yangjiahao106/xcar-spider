#! python3
# __author__ = "YangJiaHao"
# date: 2018/3/11
import json
from spider_helper import XCarSpider
from mysql_helper import MysqlHelper


def save_to_mysql():
    my_sql_helper = MysqlHelper(user='root', passwd='225669', host='192.168.1.229', db='xcar')  # 创建数据库工具对象

    max_id = my_sql_helper.search('select id from cars order by id desc limit 1')  # 查找 表cars中最大的id
    car_id = max_id[0][0] + 1 if max_id and max_id[0] else 0 # car的主键值

    my_sql_helper.connect()  # 连接数据库
    with open('result.txt', 'r') as f:
        for line in f:  # 迭代读取文件，减小内存开销。
            dic = json.loads(line)
            sql_car = 'insert into cars(id,name,brand,level,star) values({},"{}","{}","{}",{})'. \
                format(car_id, dic['name'], dic['brand'], dic['level'], dic['star'])
            my_sql_helper.insert(sql_car)  # cars中插入数据

            for model in dic['models']:
                sql_models = 'insert into models(model, gearbox, motor, power, guiding_price, seater, oil_consumption, car_id) ' 'values("{}","{}","{}",{},{},{},{},{})'.format(
                    model['model'], model['gearbox'], model['motor'], model['power'], model['guiding_price'],
                    model['seater'], model['oil_consumption'], car_id)
                my_sql_helper.insert(sql_models)  # models 中插入数据

            car_id += 1


    my_sql_helper.close()  # 关闭数据库连接



def main():
    my_spider = XCarSpider()
    my_spider.run(start_page=1, end_page=20, max_threading=4)
    save_to_mysql()


if __name__ == '__main__':
    main()
