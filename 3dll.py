# encoding=utf-8

import os
import time
import bs4
import requests
import json
from collections import OrderedDict


class LiuLiu(object):
    """
    download files from http://www.3d66.com/
    """

    PARSER = 'html.parser'

    def __init__(self):
        self.base_url = 'http://www.3d66.com'
        self.download_url_template = 'http://api.3d66.com/gateway.asp?service=ll.user.downres&llid=' \
                                     '{res_id}&rtype=0&token=xUxRxHtTx4AVy4bUxE5WyA2&t={timestamp}'
        self.models = OrderedDict()

    def get_models(self):
        r = requests.get(self.base_url)
        r.encoding = r.apparent_encoding
        s = bs4.BeautifulSoup(r.text, LiuLiu.PARSER)
        for h5 in s.find_all('h5', class_='name name1 clearfix'):
            try:
                a = h5.find('a')
                # print a['href']
                span = a.find('span')
                # print span.string
                self.models[a['href']] = span.string
            except:
                continue
                # print self.models

    @staticmethod
    def check_dir(model_type, detail_name=''):
        if not os.path.exists(model_type):
            os.mkdir(model_type)
        if not os.path.exists(model_type + os.sep + detail_name):
            os.mkdir(model_type + os.sep + detail_name)

    def get_next_page_url(self, curr_page):
        pagenav = curr_page.find('div', id='softpagenav')
        if pagenav:
            for a in pagenav.find_all('a'):
                try:
                    if a.string == u'下一页':
                        return a['href']
                except:
                    continue
        return None

    def download_one_model_type(self, model_url, model_name):
        r = requests.get(self.base_url + model_url)
        r.encoding = r.apparent_encoding
        s = bs4.BeautifulSoup(r.text, LiuLiu.PARSER)
        next_page = self.get_next_page_url(s)
        for li in s.find_all('div', class_='libox item'):
            try:
                a = li.find('a')
                if a:
                    model_detail_url = a['href']
                    print model_detail_url
                    res_id = model_detail_url[model_detail_url.rfind('/') + 1: model_detail_url.rfind('.')]
                    img = a.find('img')
                    if img:
                        print img['data-src'], img['alt']
                        img_url = img['data-src']
                        detail_type_name = img['alt']
                        self.check_dir(model_name, detail_type_name)
                        img_r = requests.get(img_url)
                        self.check_dir(model_name + '/' + detail_type_name, res_id)

                        with open(model_name + '/' + detail_type_name + '/' + str(res_id) + '.jpg', "wb") as code:
                            code.write(img_r.content)
                        rar_r = requests.get(
                            self.download_url_template.format(res_id=res_id, timestamp=int(time.time() * 1000)))
                        print rar_r.text
                        ret = json.loads(rar_r.text)
                        print ret
                        if 'msg' not in ret or 'code' not in ret or 'url' not in ret:
                            continue
                        if ret['code'] == 0:
                            real_rar = requests.get(ret['url'])
                            with open(model_name + '/' + detail_type_name + '/' + str(res_id) + '/' + str(res_id) + '.rar',
                                      "wb") as code:
                                code.write(real_rar.content)
                        else:
                            print '第二次请求'
                            rar_r = requests.get(
                                self.download_url_template.format(res_id=res_id, timestamp=int(time.time() * 1000)))
                            # print rar_r.text
                            ret = json.loads(rar_r.text)
                            if ret['code'] == 0:
                                real_rar = requests.get(ret['url'])
                                with open(model_name + '/' + detail_type_name + '/' + str(res_id) + '/' + str(
                                        res_id) + '.rar', "wb") as code:
                                    code.write(real_rar.content)
            except:
                continue

        if next_page:
            self.download_one_model_type(next_page, model_name)

    def download(self):
        self.get_models()
        for model_url, model_name in self.models.iteritems():
            print model_url, model_name
            self.download_one_model_type(model_url, model_name)


if __name__ == '__main__':
    LiuLiu().download()

