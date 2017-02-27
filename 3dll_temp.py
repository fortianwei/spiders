# encoding=utf-8

import requests
import time
import json
import os


if __name__ == '__main__':
    download_url_template = 'http://api.3d66.com/gateway.asp?service=ll.user.downres&llid=' \
                            '{res_id}&rtype=0&token=xUxRxHtTx4AVy4bUxE5WyA2&t={timestamp}'
    with open('urls.txt', 'r') as f:
        urls = f.readlines()
        for url in urls:
            url = url.strip()
            print 'url ', url
            try:
                res_id = url[url.rfind('/') + 1: url.rfind('.')]
                file_name = str(res_id) + '.rar'
                download_url = download_url_template.format(res_id=res_id, timestamp=int(time.time() * 1000))
                ret = requests.get(download_url)
                ret_t = json.loads(ret.text)
                print ret_t
                if ret_t['code'] == 0:
                    rar = requests.get(ret_t['url'])
                    with open(file_name, 'wb') as ff:
                        ff.write(rar.content)
                    os.system('unrar.exe x ' + file_name)
                else:
                    print 'request for second time'
                    ret = requests.get(download_url)
                    ret_t = json.loads(ret.text)
                    if ret_t['code'] == 0:
                        rar = requests.get(ret_t['url'])
                        with open(file_name, 'wb') as ff:
                            ff.write(rar.content)
                        os.system('unrar.exe x ' + file_name)
                print 'download ', url, ' ok'
            except:
                continue
