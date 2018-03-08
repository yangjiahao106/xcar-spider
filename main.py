#! python3
# -*- coding: UTF-8 -*-
import requests
import re
import random
from lxml import etree

result = []
# etc = {'拉普多 2016款 2.7L 手动基本型': {
#     'name': '拉普多',
#     'brand': '一汽丰田',
#     'model': '2016款 2.7L 手动基本型',
#     'level': '中大型suv',
#     'gearbox': '自动',
#     'power': 169,
#     'motor': '169kW(2.0L涡轮增压)',
#     'reference_price': 369800,
#     'guiding_price': 369800,
#     'seater': 5,
#     'oil_consumption': 7.6,
#     'star': 4.96,
# }}

headers = [
    {'User-Agent': 'Opera / 9.80(WindowsNT6.1;U;en)Presto / 2.8.131Version / 11.11'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0)'}]


def get_and_parser_html(url):
    """根据url，获取html 并将html解析成xml返回xml
    :param url: str about url
    :return: xml object
    """
    try:
        req = requests.get(url=url, headers=headers[random.randint(0, 3)])
        xml = etree.HTML(req.content.decode('GBK'))
        return xml
    except Exception as E:
        print('Get and parser url error:{0}. url:{1}'.format(E, url))


def get_car_url(page):
    """获取某一页所有汽车url的后缀，如：/166
    :param page: int
    :return: list contain urls.
    """
    url = 'http://newcar.xcar.com.cn/car/0-0-0-0-0-0-7-0-0-0-0-' + str(page)
    xpath_car_id = '//div[contains(@class, "car_col2")]/a/@href'
    xml = get_and_parser_html(url)
    urls = xml.xpath(xpath_car_id)
    return urls


def get_car_detail(url, xml):
    """获取该车的信息,name,brand,level,star
    :param url: str about this car's url
    :param xml: xml object
    :return: list contain name brand, level, star
    """
    name = xpath_extract(xml, '//div[@class="tt_h1"]/h1/text()')
    brand = xpath_extract(xml, '//div[@class="tt_h1"]/span[@class="lt_f1"]/text()')
    level = xpath_extract(xml, '//div[@class="ref_par"]/ul/li[1]/text()')
    star = get_star(url)

    return [name, brand, level, star]


def get_car_detail_models_url(car_url):
    """
    获取该车的信息,和所有型号的url后缀，如：/m2331
    :param car_url: url
    :return: a list contain urls, a list contain detail
    """
    url = 'http://newcar.xcar.com.cn' + car_url
    xml = get_and_parser_html(url)
    car_models_urls = xml.xpath('//tr[@class = "table_bord"]/td[1]/p[1]/a[1]/@href')
    car_detail = get_car_detail(url, xml)  # 获取车辆的 名称，品牌，级别,评价 返回list
    return car_models_urls, car_detail


def get_star(url):
    """获取评价
    :param url: str
    :return: int
    """
    url = url + 'review.htm'
    print(url)
    xml = get_and_parser_html(url)
    stars = xml.xpath('//div[@class="column"]//div[@class="bg"]/div/text()')
    star = count = 0
    if len(stars) > 1:
        for each in stars:  # 合成综合评分。
            try:
                star += float(each[:4])
                count += 1
            except:
                print('get star error,url:', url)
        return round(star / count, 2)  # 保留两位小数
    else:
        return None


def xpath_extract(xml, xpath, **kwargs):
    """根据xpath和regex从xml中提取信息
    :param xml: xml object
    :param xpath:str about xpath
    :param kwargs: regex
    :return:
    """
    demo = xml.xpath(xpath)
    demo = demo[0] if len(demo) == 1 else None
    if demo and kwargs.get('regex'):  # 如果参数不为空，并且参数中有正则表达式
        demo = re.search(kwargs.get('regex'), demo)
        demo = demo.group() if demo else None
    return demo


def get_model_detail(model_url, car_detail):
    """获取车型的详细信息
    :param model_url:
    :param car_detail:
    :return: dict
    """
    url = "http://newcar.xcar.com.cn/" + model_url
    xml = get_and_parser_html(url)
    model_detail = dict()
    model_detail['name'] = car_detail[0]
    model_detail['brand'] = car_detail[1]
    model_detail['level'] = car_detail[2]
    model_detail['star'] = car_detail[3]
    model_detail['model'] = xpath_extract(xml, '//div[contains(@class,"tt_h1")]/h1/text()')
    model_detail['gearbox'] = xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[3]/em/text()')
    model_detail['motor'] = xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[4]/em/text()')
    model_detail['power'] = xpath_extract(xml, '//div[@class="ref_cn"]/ul/li[4]/em/text()', regex=r'\d+(kw|Kw|kW|KW)')
    guiding_price = xpath_extract(xml, '//div[@class="ref_cn"]//dl[@class="ref_dl2"]//em/a/text()')
    model_detail['guiding_price'] = round(float(guiding_price) * 10000, 2) if guiding_price.isdigit() else None
    model_detail['seater'] = xpath_extract(xml, '//div[@class="model_main"][2]/table[1]/tbody/tr[4]/td[2]/text()',
                                           regex=r'\d座')
    oil_consumption = xpath_extract(xml, '//div[@class="ref_cn"]/ul[@class="ref_ul"]/li[2]/em/text()')
    model_detail['oil_consumption'] = oil_consumption if oil_consumption != "暂无" else None
    return model_detail


def main():
    cars = get_car_url(1)  # 获取某一页的汽车url列表。
    for car in cars[3:4]:
        models, car_detail = get_car_detail_models_url(car)  # 获取型号的url，名字，品牌。
        for model in models[:1]:
            model_detail = get_model_detail(model, car_detail)  # 获取详细信息。
            print(model_detail)


if __name__ == '__main__':
    main()
