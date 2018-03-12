#! python3
# -*- coding: UTF-8 -*-
import re
import json
import time
import random
import requests
from lxml import etree
from threading import Lock
from concurrent import futures


# result = {'拉普多 2016款 2.7L 手动基本型': {'name': '拉普多','brand': '一汽丰田','model': '2016款 2.7L 手动基本型',
#     'level': '中大型suv','gearbox': '自动','power': 169,'motor': '169kW(2.0L涡轮增压)','reference_price': 369800,
#     'guiding_price': 369800,'seater': 5,'oil_consumption': 7.6,'star': 4.96,} }


class XCarSpider(object):
    def __init__(self):
        self.__headers = [
            {'User-Agent': 'Opera / 9.80(WindowsNT6.1;U;en)Presto / 2.8.131Version / 11.11'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
            {'User-Agent': 'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0)'}]
        self.write_lock = Lock()
        self.num_lock = Lock()
        self.car_num = 0
        self.count = 0

    def run(self, start_page, end_page, max_threading=1):
        """启动程序
        :param start_page: int
        :param end_page: int
        :param max_threading:int
        """
        self.car_num = (end_page - start_page + 1) * 20
        pool = futures.ThreadPoolExecutor(max_threading)
        pool.map(self.__get_one_page, [i for i in range(start_page, end_page + 1)])
        pool.shutdown(wait=True)

    def __get_one_page(self, page):
        """获取一页汽车的所有车型的信息
        :param page: int
        :return: None
        """
        cars = self.__get_car_url(page)  # 获取某一页的汽车url列表。
        for car in cars[:2]:
            model_urls, car_detail = self.__get_model_urls_and_car_detail(car)  # 获取型号的url，名字，品牌。

            res = {}
            res['name'] = car_detail[0]
            res['brand'] = car_detail[1]
            res['level'] = car_detail[2]
            res['star'] = car_detail[3]

            all_models_detail = []
            for url in model_urls:
                model_detail = self.__get_model_detail(url)  # 获取详细信息。
                all_models_detail.append(model_detail)
                res['models'] = all_models_detail
            self.__save_to_file(res)
            self.__print_progress()
            time.sleep(5)

    def __print_progress(self):
        # 打印进度。
        self.num_lock.acquire()
        self.count += 1
        self.num_lock.release()
        progress = round((self.count / self.car_num * 100), 2)
        print('\r已完成:{}%'.format(progress), end='')
        if self.count >= self.car_num:
            print('\n任务已完成。')

    def __save_to_file(self, res):
        """保存一款车所有车型的信息。
        :param res:list contains dict
        """
        try:
            self.write_lock.acquire()
            with open('./result.txt', 'a', encoding='utf-8') as f:
                json.dump(res, f)
                f.write('\n')
            self.write_lock.release()
        except Exception as e:
            print('write to file error:', e)

    def __get_and_parser_html(self, url):
        """根据url，获取html 并将html解析成xml返回xml
        :param url: string
        :return: xml object
        """
        try:
            req = requests.get(url=url, headers=self.__headers[random.randint(0, 3)])
            xml = etree.HTML(req.content.decode('GBK'))
            return xml
        except Exception as E:
            print('Get and parser url error:{0}. url:{1}'.format(E, url))

    def __get_car_url(self, page):
        """获取某一页所有汽车url的后缀，如：/166
        :param page: int
        :return: list contain urls.
        """
        url = 'http://newcar.xcar.com.cn/car/0-0-0-0-0-0-7-0-0-0-0-' + str(page)
        xpath_car_id = '//div[contains(@class, "car_col2")]/a/@href'
        xml = self.__get_and_parser_html(url)
        urls = xml.xpath(xpath_car_id)
        return urls

    def __get_car_detail(self, url, xml):
        """获取该车的信息,name,brand,level,star
        :param url: str about this car's url
        :param xml: xml object
        :return: list contain name brand, level, star
        """
        name = self.__xpath_extract(xml, '//div[@class="tt_h1"]/h1/text()')
        brand = self.__xpath_extract(xml, '//div[@class="tt_h1"]/span[@class="lt_f1"]/text()')
        level = self.__xpath_extract(xml, '//div[@class="ref_par"]/ul/li[1]/text()')
        star = self.__get_star(url)
        return [name, brand, level, star]

    def __get_model_urls_and_car_detail(self, car_url):
        """
        获取该车的信息,和所有型号的url后缀，如：/m2331
        :param car_url: url
        :return: a list contain urls, a list contain detail
        """
        url = 'http://newcar.xcar.com.cn' + car_url
        xml = self.__get_and_parser_html(url)
        car_models_urls = xml.xpath('//tr[@class = "table_bord"]/td[1]/p[1]/a[1]/@href')
        car_detail = self.__get_car_detail(url, xml)  # 获取车辆的 名称，品牌，级别,评价 返回list
        return car_models_urls, car_detail

    def __get_star(self, url):
        """获取评价
        :param url: str
        :return: int
        """
        url = url + 'review.htm'
        xml = self.__get_and_parser_html(url)
        stars = xml.xpath('//div[@class="column"]//div[@class="bg"]/div/text()')
        star = count = 0
        if len(stars) >= 1:
            for each in stars:  # 合成综合评分。
                try:
                    star += float(each[:4])
                    count += 1
                except:
                    print('get star error,url:', url)
            return round(star / count, 2)  # 保留两位小数
        else:
            return 'null'

    @staticmethod
    def __xpath_extract(xml, xpath, **kwargs):
        """根据xpath和regex从xml中提取信息
        :param xml: xml object
        :param xpath:string about xpath
        :param kwargs: regex, type
        :return:
        """
        demo = xml.xpath(xpath)
        demo = demo[0] if len(demo) == 1 else 'null'

        if demo and kwargs.get('regex'):  # 如果参数不为空，并且参数中有正则表达式
            demo = re.search(kwargs.get('regex'), demo)
            demo = demo.groups()[0] if demo and demo.groups() else 'null'

        if demo and kwargs.get('type'):
            if kwargs.get('type') == float:
                try:
                    demo = round(float(demo), 2)
                except:
                    demo = 'null'
            elif kwargs.get('type') == int:
                try:
                    demo = int(demo)
                except:
                    demo = 'null'
        return demo

    def __get_model_detail(self, model_url):
        """获取车型的详细信息
        :param model_url:
        :param car_detail:
        :return: dict
        """
        url = "http://newcar.xcar.com.cn/" + model_url
        xml = self.__get_and_parser_html(url)
        model_detail = dict()
        model_detail['model'] = self.__xpath_extract(xml, '//div[contains(@class,"tt_h1")]/h1/text()')
        model_detail['gearbox'] = self.__xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[3]/em/text()')
        model_detail['motor'] = self.__xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[4]/em/text()')
        model_detail['power'] = \
            self.__xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[4]/em/text()',
                                 regex=r'(\d+)',type=int)
        model_detail['guiding_price'] = \
            self.__xpath_extract(xml, '//div[@class="ref_cn"]//dl[@class="ref_dl2"]//em/a/text()', type=float)
        model_detail['seater'] = \
            self.__xpath_extract(xml,'//div[@class="model_main"][2]/table[1]/tbody/tr[4]/td[2]/text()',
                                 regex=r'(\d+)座', type=int)
        model_detail['oil_consumption'] = \
            self.__xpath_extract(xml, '//div[@class="ref_cn"]/ul[@class="ref_ul"]/li[2]/em/text()',
                                 regex='(\d+.*\d*)L', type=float)
        return model_detail


if __name__ == '__main__':
    my_spider = XCarSpider()
    my_spider.run(start_page=1, end_page=2, max_threading=2)
