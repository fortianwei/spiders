#encoding=utf-8
import requests
import requests.exceptions
import bs4
import os
import re
import time
url = 'http://www.360msl.com/?page_id=118&paged={}'
start_r = requests.get(url)
# print r.text
#find the max paged number
start_soup = bs4.BeautifulSoup(start_r.text, 'html.parser')
topics = []
for x in start_soup.find_all('div', class_='wpb_wrapper'):
    # print x
    for y in x.find_all('a', class_='medium'):
        topics.append((y['href'], y.string))

for topic in topics:
    topic_url, topic_name = topic
    if topic_url.find('118') > 0:
        print 'topic ', topic_name, ' passed this time'
        continue
    print 'topic_name is ', topic_name
    current_dir = topic_name
    if not os.path.exists(current_dir):
        os.mkdir(current_dir)
    first_r = requests.get(topic_url)
    first_soup = bs4.BeautifulSoup(first_r.text, 'html.parser')
    paged_list = []
    for i in first_soup.find_all('a', class_='page-numbers'):
        print i.string
        if i.string.isdigit():
            paged_list.append(int(str(i.string)))
    print paged_list
    max_paged = max(paged_list)

    for paged_number in range(27, max_paged + 1):
        print 'page ', str(paged_number), ' start'
        temp_paged_url = url.format(url.format(paged_number))
        r = requests.get(temp_paged_url)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        print soup.find_all('div', class_='content')
        for j in soup.find_all('h5', attrs={'itemprop': 'name'}):
            # try:
                temp_url, temp_dir = j.contents[0]['href'], j.contents[0].string
                if not os.path.exists(current_dir + '/' + temp_dir):
                    os.mkdir(current_dir + '/' + temp_dir)
                if os.listdir(current_dir + '/' + temp_dir):
                    print 'already downloaded'
                    continue
                print 'start with ', temp_dir
                print 'url is ', temp_url
                temp_r = requests.get(temp_url)
                temp_soup = bs4.BeautifulSoup(temp_r.text, 'html.parser')
                # temp_weixin = temp_soup.find(href=re.compile('mp\.weixin'))
                temp_weixin = temp_soup.find('strong', string='微信公众平台图片链接限制')
                if not temp_weixin:
                    print 'no mp.weixin, an old page'
                    last_soup = temp_soup
                    all_imgs = last_soup.find_all('img', attrs={'data-src': re.compile('qpic')})
                    older = False
                    if not all_imgs:
                        all_imgs = last_soup.find_all('img', attrs={'src': re.compile('qpic')})
                        if not all_imgs:
                            continue
                        older = True
                    img_index = 1
                    for img_tag in all_imgs:
                        try:
                            img_url = img_tag['src' if older else 'data-src']
                            print 'img_url is ', img_url
                            img_src = requests.get(img_url)
                            with open(current_dir + '/' + temp_dir+'/' + str(img_index) + '.png', "wb") as code:
                                code.write(img_src.content)
                            # time.sleep(0.01)
                            img_index += 1
                        except requests.exceptions.ChunkedEncodingError:
                            print 'connection reset... just continue'
                            continue
                else:
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
                            if img_url.find('wx_lazy') > 0:
                                img_url = img_url[:img_url.find('?')]
                            # print 'img_url is ', img_url
                            img_src = requests.get(img_url)
                            with open(current_dir + '/' + temp_dir+'/' + str(img_index) + '.png', "wb") as code:
                                code.write(img_src.content)
                            img_index += 1
                print 'total ', img_index
            # except Exception, e:
            #     print e.message
            #     continue
        print 'page ', paged_number, ' end'




