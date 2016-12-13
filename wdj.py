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

sql_insert_res = u'''
insert into resources(RES_LOCATION, RES_PACKAGENAME, RES_NAME, RES_ICONS, RES_STATUS, RES_DESCRIPTION,
RES_FREEPAID,RES_UPDATEDATE,RES_VERSION,RES_DOWNLOADNUM,RES_CAPACITY,RES_DEVELOPER,RES_RATED,RES_SCREENSHOTS,
RES_TYPE,RES_RANK) select '{location}','{packagename}','{name}','{icon}',1,'{desc}',0, now(),'{version}',{downnum},{capacity},
'{developer}',{rated},'{screenshots}', {category},0 from dual where not exists(
select RES_PACKAGENAME from resources where RES_PACKAGENAME='{packagename}')
'''
sql_insert_tag_res_relation = '''
insert into resources_category_relationship(RESCATEGORY_ID,RES_ID) values({category_id}, {res_id})
'''
sql_check_if_exists_packagename = '''
select RES_ID from resources where RES_PACKAGENAME='{}' limit 1
'''
TYPE_ICON = 1
TYPE_SCREEN_SHOT = 2


class WDJ(object):
    def __init__(self):
        self.icon_dir = 'upload'
        self.screenshots_dir = 'ss_small'
        self.base_url = 'http://www.wandoujia.com/category/game'
        self.conn = MySQLdb.connect(host='127.0.0.1', port=3306, db='mystore',
                                    user='tianwei', passwd='tianwei', charset='utf8')

        self.conn.autocommit(1)
        self.cursor = self.conn.cursor()
        self.tag_map = {}
        self.cursor.execute('select RESCATEGORY_ID,RESCATEGORY_NAME from resources_category where RESCATEGORY_ID>155')
        for tag in self.cursor.fetchall():
            self.tag_map[tag[1]] = tag[0]

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
                # print 'parent tag ', parent_tag
                parent_tag_row_id = self.cursor.lastrowid
                # print 'row id ', str(parent_tag_row_id)
                child_tags = t.find('div', class_='child-cate')
                if child_tags:
                    for child_tag in [i['title'] for i in child_tags.findAll('a')]:
                        # print child_tag
                        self.cursor.execute(sql_insert_tag.format(child_tag, parent_tag_row_id))
                        tag_row_id = self.cursor.lastrowid
                        # print 'child tag row id ', tag_row_id

    def download_img(self, url, type=TYPE_SCREEN_SHOT):
        # print 'url ', url
        split = url.split('/')
        split_arr = split[-3:]
        # print 'split arr ', split_arr
        img_parent_dir = self.icon_dir if type == TYPE_ICON else self.screenshots_dir
        dirs = img_parent_dir + os.sep + split_arr[0] + os.sep + split_arr[1]
        # print 'dirs ', dirs
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        img_src = requests.get(url)
        with open(dirs + os.sep + str(split_arr[-1]), "wb") as code:
            code.write(img_src.content)

    def fetch_info_from_app_detail_url(self, parent_tag_name, child_tag_name, url):
        packagename = url[url.rindex('/') + 1:]
        self.cursor.execute(sql_check_if_exists_packagename.format(packagename))
        packagename_exists = self.cursor.fetchone()
        if packagename_exists:
            return
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        # print soup.prettify()
        detail_wrap = soup.find('div', class_='detail-wrap')

        if detail_wrap:
            icon = detail_wrap.find('img', attrs={'itemprop': 'image'})['src']
            name = detail_wrap.find('span', attrs={'itemprop': 'name'}).string
            screen_all = detail_wrap.findAll('img', attrs={'itemprop': 'screenshot'})
            screen_shots = ','.join([screen_tag['src'] for screen_tag in screen_all])

            desc_tag = detail_wrap.find('div', attrs={'itemprop': 'description'})
            download_url = detail_wrap.find('div', class_='download-wp').find('a')[
                               'href'] + '?source=wandoujia-web_inner_referral_binded'
            downnum = detail_wrap.find('i', attrs={'itemprop': 'interactionCount'})['content'][len('UserDownloads:'):]

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

            self.download_img(icon, type=TYPE_ICON)
            for screen_shot in screen_shots.split(','):
                self.download_img(screen_shot, type=TYPE_SCREEN_SHOT)
            screen_shots = ','.join(
                [(self.screenshots_dir + os.sep + '/'.join(sc.split('/')[-3:])) for sc in screen_shots.split(',')])
            icon = self.icon_dir + os.sep + '/'.join(icon.split('/')[-3:])
            # print icon
            # print name
            # print screen_shots
            # print desc
            # print publish_date
            # print download_url
            # print downnum
            # print apk_size
            # print version_name
            # print developer

            # RES_SCREENSHOTS,RES_TYPE,RES_RANK) values('{location}','{packagename}','{name}','{icon}',1,'{desc}',
            # 0, '{version}',{downnum},{capacity},'{developer}',{rated},'{screenshots}', {category},{rank})

            sql = sql_insert_res.format(location=download_url, packagename=packagename, name=name,
                                        icon=icon, desc=desc, version=version_name, downnum=downnum, capacity=apk_size,
                                        developer=developer, rated=3, screenshots=screen_shots,
                                        category=self.tag_map[parent_tag_name])
            rows_affected = self.cursor.execute(sql)
            print 'rows_affected ', rows_affected
            if rows_affected:
                res_id = self.cursor.lastrowid
                self.cursor.execute(
                    sql_insert_tag_res_relation.format(category_id=self.tag_map[child_tag_name], res_id=res_id))

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
                            try:
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
                                        self.fetch_info_from_app_detail_url(parent_tag, child_tag_name, app_detail_url)
                            except:
                                print 'ERROR with something,continue with next app'
                                continue


if __name__ == '__main__':
    WDJ().get_apk_info()
