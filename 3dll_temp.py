# encoding=utf-8

import requests
import time
import json


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
                download_url = download_url_template.format(res_id=res_id, timestamp=int(time.time() * 1000))
                ret = requests.get(download_url)
                ret_t = json.loads(ret.text)
                print ret_t
                if ret_t['code'] == 0:
                    rar = requests.get(ret_t['url'])
                    with open(str(res_id) + '.rar', 'wb') as ff:
                        ff.write(rar.content)
                else:
                    print 'request for second time'
                    ret = requests.get(download_url)
                    ret_t = json.loads(ret.text)
                    if ret_t['code'] == 0:
                        rar = requests.get(ret_t['url'])
                        with open(str(res_id) + '.rar', 'wb') as ff:
                            ff.write(rar.content)
                print 'download ', url, ' ok'
            except:
                continue
