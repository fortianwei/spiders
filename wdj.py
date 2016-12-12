# encoding=utf-8

import requests
import bs4
from bs4.element import Tag
import os
import MySQLdb
import time

sql_insert_tag = u'''
insert into resources_category(RESCATEGORY_NAME,RESCATEGORY_PARENTCATEGORYID) values('{}',{})
'''


class WDJ(object):
    def __init__(self):
        self.base_url = 'http://www.wandoujia.com/category/game'
        self.conn = MySQLdb.connect(host='127.0.0.1', port=3306, db='mystore',
                                    user='tianwei', passwd='tianwei', charset='utf8')
        self.conn.autocommit(1)
        self.cursor = self.conn.cursor()

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
                parent_tag = t.find('a', class_='cate-link')['title']
                self.cursor.execute(sql_insert_tag.format(parent_tag, 0))
                print 'parent tag ', parent_tag
                parent_tag_row_id = self.cursor.lastrowid
                print 'row id ', str(parent_tag_row_id)
                child_tags = t.find('div', class_='child-cate')
                if child_tags:
                    for child_tag in [i['title'] for i in child_tags.findAll('a')]:
                        print child_tag
                        self.cursor.execute(sql_insert_tag.format(child_tag, parent_tag_row_id))
                        tag_row_id = self.cursor.lastrowid
                        print 'child tag row id ', tag_row_id

    def fetch_info_from_app_detail_url(self, url):
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        # print soup.prettify()
        detail_wrap = soup.find('div', class_='detail-wrap')

        if detail_wrap:
            icon = detail_wrap.find('img', attrs={'itemprop': 'image'})['src']
            name = detail_wrap.find('span', attrs={'itemprop': 'name'}).string
            screen_all = detail_wrap.findAll('img', attrs={'itemprop': 'screenshot'})
            desc_tag = detail_wrap.find('div', attrs={'itemprop': 'description'})
            download_url = detail_wrap.find('div', class_='download-wp').find('a')[
                               'href'] + '?source=wandoujia-web_inner_referral_binded'

            desc = ''
            for e in desc_tag.recursiveChildGenerator():
                if isinstance(e, basestring):
                    desc += e.strip()
                elif e.name == 'br':
                    desc += '\n'

            infos_list = detail_wrap.find('dl', class_='infos-list')
            dds = infos_list.findAll('dd')
            apk_size = dds[0].meta['content']
            # apk_size = int(apk_size[:-2]) * {'G': 1024 ** 3, 'M': 1024**2, 'K': 1024}[apk_size[-1]]
            publish_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dds[3].string, u'%Y年%m月%d日'))
            version_name = dds[4].string
            # dds[5]
            # icon = detail_wrap.find('img', attrs={'itemprop': 'image'})['src']
            developer = dds[6].span.string if dds[6].span else dds[6].a.string
            print icon
            print name
            print screen_all
            print desc
            print publish_date
            print download_url
            print apk_size
            print version_name
            print developer

    def get_apk_info(self):
        resp = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        tag_box = soup.find('ul', class_='tag-box').children
        for t in tag_box:
            if type(t) == Tag:
                parent_tag = t.find('a', class_='cate-link')['title']
                print parent_tag
                child_tags = t.find('div', class_='child-cate')
                if child_tags:
                    for child_tag in child_tags.findAll('a'):
                        child_tag_url, child_tag_name = child_tag['href'], child_tag['title']
                        print '当前子分类', child_tag_name, ' 当前子分类url ', child_tag_url
                        for i in range(1, 1000):
                            temp_child_tag_url = child_tag_url + (('_' + str(i)) if i > 1 else '')
                            print 'paged url ', temp_child_tag_url
                            child_tag_resp = requests.get(temp_child_tag_url)
                            if child_tag_resp.status_code == 404:
                                print 'url ', temp_child_tag_url, ' not found, break'
                                break
                            child_tag_soup = bs4.BeautifulSoup(child_tag_resp.text, 'html.parser')
                            apps_ul = child_tag_soup.find('ul', id='j-tag-list')
                            if apps_ul:
                                for app_h2 in apps_ul.findAll('h2', 'app-title-h2'):
                                    app_detail_url = app_h2.find('a')['href']
                                    print 'app detail url ', app_detail_url
                                    self.fetch_info_from_app_detail_url(app_detail_url)


if __name__ == '__main__':
    WDJ().get_apk_info()
