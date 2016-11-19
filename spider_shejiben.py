#encoding=utf-8

import requests
import bs4
import os
base_url = 'http://www.shejiben.com/'
url = base_url + 'works/'

first_r = requests.get(url)
first_soup = bs4.BeautifulSoup(first_r.text, 'html.parser')
styles = first_soup.find_all('div', class_='spaceList')[1]
for style in styles.find_all('a'):
    style_url, style_name = style['href'], style.string
    if not os.path.exists(style_name):
        os.mkdir(style_name)

    style_r = requests.get(style_url)
    style_soup = bs4.BeautifulSoup(style_r.text, 'html.parser')
    styles = style_soup.find('div', class_='spaceList')
    for space_with_style in styles.find_all('a'):
        space_with_style_url, space_name = space_with_style['href'], space_with_style.string
        if not os.path.exists(style_name + '/' + space_name):
            os.mkdir(style_name + '/' + space_name)
        print 'space_with_style_url is ', space_with_style_url
        space_with_style_r = requests.get(space_with_style_url)
        space_with_style_soup = bs4.BeautifulSoup(space_with_style_r.text, 'html.parser')

        max_page = max([int(page.string) if page.string and page.string.isdigit() else 0 for
                        page in space_with_style_soup.find('p', class_='page_num').find_all('a')])
        print 'total page num is ', max_page

        for page_num in range(max_page):
            # one page
            paged_url = space_with_style_url + 'p' + str(page_num * 48)
            print 'page url is ', paged_url
            paged_url_r = requests.get(paged_url)
            paged_url_soup = bs4.BeautifulSoup(paged_url_r.text, 'html.parser')
            for detail_page in paged_url_soup.find_all('div', 'gradual'):
                # one link
                link = detail_page.find('a')
                detail_url, detail_name = base_url + link['href'], link.string
                detail_num = detail_url[detail_url.rfind('/') + 1:detail_url.rfind('.')]
                detail_name = detail_name + '_' + detail_num
                print 'detail url is ', detail_url, ' detail name is ', detail_name
                detail_dir = style_name + '/' + space_name + '/' + detail_name
                if not os.path.exists(detail_dir):
                    os.mkdir(detail_dir)
                else:
                    print 'has downloaded:', detail_dir
                    continue
                try:
                    detail_r = requests.get(detail_url)
                except:
                    print 'request for detail failed, just continue'
                    continue
                detail_soup = bs4.BeautifulSoup(detail_r.text, 'html.parser')
                image_list_htmls = detail_soup.find('ul', 'image-list')
                img_index = 0
                for image_a in image_list_htmls.find_all('a'):
                    # images in one link
                    img_html_url, html_name = base_url + image_a['href'], image_a.find('img')['alt']
                    html_num = img_html_url[img_html_url.rfind('/') + 1:img_html_url.rfind('.')]
                    html_name = html_name + '_' + html_num if html_name.find(html_num) < 0 else html_name
                    # print 'img_html_url ', img_html_url, ' html_name ', html_name
                    try:
                        single_html_r = requests.get(img_html_url)
                    except:
                        print 'request for single html failed, just continue'
                        continue
                    single_html_soup = bs4.BeautifulSoup(single_html_r.text, 'html.parser')
                    img_li = single_html_soup.find('li', 'nowPic')
                    if not img_li:
                        print 'no img_li'
                        continue
                    img_url = img_li.find('img')['src']
                    # print 'last img url is ', img_url
                    try:
                        img_src = requests.get(img_url)
                    except:
                        print 'request for final img failed, just continue'
                        continue
                    with open(detail_dir+'/' + html_name + '.jpg', "wb") as code:
                        code.write(img_src.content)
                    img_index += 1
                print 'img total ', str(img_index)







