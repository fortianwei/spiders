# encoding = utf-8
import os
import sys
import bs4
import requests


class Houzz(object):
    """
    download  pictures in houzz.com
    """

    PARSER = 'html.parser'

    def __init__(self):
        self.base_url = 'http://www.houzz.com/photos/'
        self.rooms = []
        self.styles = []

    def get_styles_and_rooms(self):
        r = requests.get(self.base_url)
        s = bs4.BeautifulSoup(r.text, Houzz.PARSER)
        room_ul = s.find('ul', attrs={'id': 'roomFilter'})
        for a in room_ul.find_all('a', class_='sidebar-item-label'):
            if a['href'].startswith('http'):
                self.rooms.append([a['href'], a.string, a['href'][a['href'].rfind('/') + 1:]])

        styles_ul = s.find('ul', attrs={'id':'styleFilter'})
        for a in styles_ul.find_all('a', class_='sidebar-item-label'):
            if a['href'].startswith('http'):
                self.styles.append([a['href'], a.string])

        print self.rooms
        print self.styles

    @staticmethod
    def check_dir(style, room):
        if not os.path.exists(style):
            os.mkdir(style)
        if not os.path.exists(style + os.sep + room):
            os.mkdir(style + os.sep + room)

    def download(self):
        self.get_styles_and_rooms()
        for style in self.styles:
            for room in self.rooms:
                # print 'current style & room is ', style, ' ', room
                Houzz.check_dir(style[1], room[1])

                url_with_style_and_room = style[0] + '/' + room[2]
                print 'url_with_style_and_room url is ', url_with_style_and_room
                try:
                    r = requests.get(url_with_style_and_room)
                except (Exception, IOError):
                    print 'request for style&room failed ,continue'
                    continue
                s = bs4.BeautifulSoup(r.text, Houzz.PARSER)
                all_page_numbers = s.find('div', class_='allPageNumbers')
                max_page_number = max([int(a.string) for a in all_page_numbers.find_all('a', class_='pnSmall')])
                print 'page total:', str(max_page_number)
                img_index = 0
                style_room_downloaded_urls = []
                for page in xrange(0, max_page_number):
                    print 'page start:', str(page)
                    paged_url = url_with_style_and_room + '/p' + str(page * 8)
                    try:
                        page_r = requests.get(paged_url)
                    except (Exception, IOError):
                        print 'request for page ,continue'
                        continue
                    page_s = bs4.BeautifulSoup(page_r.text, Houzz.PARSER)
                    pic_list_div = page_s.find('div', class_='browseListBody')
                    if not pic_list_div:
                        print 'no pic_list_div found,continue'
                        continue
                    for img in pic_list_div.find_all('img', class_= 'space'):
                        img_url = img['src']
                        print 'download img url is ', img_url
                        if img_url in style_room_downloaded_urls:
                            print 'has downloaded! continue'
                        try:
                            img_src = requests.get(img_url)
                            style_room_downloaded_urls.append(img_url)
                        except (Exception, IOError):
                            print 'download img error,continue'
                            continue
                        with open(style[1] + '/' + room[1] + '/' + str(img_index) + '.jpg', "wb") as code:
                            code.write(img_src.content)
                        img_index += 1



if __name__ == '__main__':
    Houzz().download()
