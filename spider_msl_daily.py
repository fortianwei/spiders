# encoding=utf-8
import requests
import requests.exceptions
import bs4
import os
import re

url_template = 'http://www.360msl.com/?p={}'
default_start_page = 10928


def get_latest_page():
    temp_url = url_template.format(default_start_page)
    temp_r = requests.get(temp_url)
    temp_soup = bs4.BeautifulSoup(temp_r.text, 'html.parser')
    recent_post_mini_div = temp_soup.find('div', class_='recent-post-mini')
    recent_a = recent_post_mini_div.find('a')
    # print recent_post_mini_div
    # print recent_a
    href = recent_a['href']
    return int(href[href.index('p=') + 2:])


def get_start_page():
    if os.path.exists('page'):
        with open('page') as f:
            return f.readline()
    return default_start_page


def record_page(page):
    with open('page', 'w') as f:
        f.writelines(str(page))


def start_crawler():
    start_page = int(get_start_page() or default_start_page)
    end_page = get_latest_page()
    if not os.path.exists('msl'):
        os.mkdir('msl')

    # print start_page
    # print end_page
    current_msl_index = None
    for i in xrange(start_page, end_page):
        try:
            if i != default_start_page:
                record_page(i)
            temp_url = url_template.format(i)
            temp_r = requests.get(temp_url)
            temp_soup = bs4.BeautifulSoup(temp_r.text, 'html.parser')
            # temp_weixin = temp_soup.find(href=re.compile('mp\.weixin'))
            temp_weixin = temp_soup.find('strong', string='微信公众平台图片链接限制')
            if temp_weixin:
                title = temp_soup.find('h3', class_='post-title').string
                msl_substr_index = title.find(u'【名师联')
                msl_qi_index = title.rfind(u'期')
                print msl_substr_index
                print msl_qi_index
                print type(msl_qi_index)
                print type(msl_substr_index)
                if msl_substr_index == -1 or msl_qi_index == -1 or msl_substr_index >= msl_qi_index:
                    if not current_msl_index:
                        continue
                else:
                    current_msl_index = title[msl_substr_index + 4:msl_qi_index]
                    print 'current_msl_index', current_msl_index
                current_index_dir = 'msl/' + str(current_msl_index)
                if not os.path.exists('msl/' + str(current_msl_index)):
                    os.mkdir(current_index_dir)
                current_dir = current_index_dir + '/' + title
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                temp_weixin = temp_soup.find(href=re.compile('mp\.weixin'))
                temp_weixin_url = temp_weixin['href']
                print 'temp weixin url is ', temp_weixin_url
                last_r = requests.get(temp_weixin_url)
                last_soup = bs4.BeautifulSoup(last_r.text, 'html.parser')
                rich_media_content = last_soup.find('div', class_='rich_media_content')
                # illegal html
                img_index = 1
                if not rich_media_content:
                    print 'article has been deleted'
                    continue
                for child in rich_media_content.descendants:
                    temp_find = child.find('img')
                    if temp_find and temp_find != -1:
                        img_url = child.find('img')['data-src']
                        # print 'img_url is ', img_url
                        if img_url.find('wx_lazy') > 0:
                            img_url = img_url[:img_url.find('?')]
                        img_src = requests.get(img_url)
                        with open(current_dir + '/' + str(img_index) + '.png', "wb") as code:
                            code.write(img_src.content)
                        img_index += 1
        except:
            continue


start_crawler()

