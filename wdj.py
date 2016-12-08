# encoding=utf-8

import requests
import bs4
from bs4.element import Tag
import os


class WDJ(object):
    def __init__(self):
        self.base_url = 'http://www.wandoujia.com/category/game'

    def get_tag_box(self):
        """
        获取豌豆荚游戏相关的大小标签
        :return:
        """
        resp = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        tag_box = soup.find('ul', class_='tag-box').children
        for t in tag_box:
            if type(t) == Tag:
                # print t
                print t.find('a', class_='cate-link')['title']
                x = t.find('div', class_='child-cate')
                # print x, type(x)
                if x:
                    print [i['title'] for i in x.findAll('a')]
                        # print y



if __name__ == '__main__':
    WDJ().get_tag_box()

