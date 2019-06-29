# coding: utf-8 
# @Time : 2019/6/29 上午 11:18 
# @Author : gyn 
# @email : guogyn@foxmail.com

# 截止至今书籍数量88588
# 以文件方式存储。或者用redis
from lxml import etree
from requests import get
from re import compile, findall
from json import dump, load
from random import choice
from traceback import format_exc
import warnings
warnings.filterwarnings('ignore')


url0 = "https://www.xbiquge6.com/"
pattern_for_catalog_link_id = compile('/(\d*?)\.')
UA = [
    # Opera
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
    'Opera/8.0 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',

    # Firefox
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',

    # Safari
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',

    # chrome
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',

    # 360
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',

    # 淘宝浏览器
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',

    #猎豹浏览器
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)',

    # QQ浏览器
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',

    # sogou浏览器
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',

    # maxthon浏览器
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',

    # UC浏览器
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36',
]


def get_headers():
    return {
        'User-Agent': choice(UA),   # sample(UA, 1)
    }


def mget(url):
    return get(url=url, headers=get_headers(), verify=False)


def get_real_book_id(book_id):
    book_id = str(book_id)
    L = len(book_id)
    if L == 5:
        return book_id[:1]+'_'+book_id
    elif L == 4:
        return book_id[0]+'_'+book_id
    elif L in [1, 2, 3]:
        return '0_' + book_id
    else:
        return '0_0'
    pass


def get_book_msg(book_id):
    url = url0+get_real_book_id(book_id)+'/'
    res = mget(url)
    if res.status_code == 200:
        html = etree.HTML(res.content)
        '''
        maininfo = html.xpath('//div[@id="maininfo"]')[0]
        book_name = maininfo.xpath('.//h1/text()')[0]
        temp = maininfo.xpath('./div[@id="info"]/p/text()')
        print(temp)
        '''
        temp = html.xpath('string(//div[@id="info"])').strip().replace('\t', '').split('\n', 1)
        book_name = temp[0]
        info = temp[1]      # 小说作者更新状态
        intro = html.xpath('string(//div[@id="intro"])').strip().split('各位书友')[0] or '暂无'   # 小说内容

        div_list = html.xpath('//div[@id="list"]')[0]
        catalogs_link = div_list.xpath('.//dd//a/@href')    # 章节链接
        catalogs_title = div_list.xpath('.//dd//a/text()')  # 章节标题
        L = len(catalogs_link)
        if L == len(catalogs_title):
            # catalogs = [findall(pattern_for_catalog_link_id, link)[0]+'@'+title.split('章 ', 1)[-1] for link, title in zip(catalogs_link, catalogs_title)]
            catalogs_link = [findall(pattern_for_catalog_link_id, link)[0] for link in catalogs_link]
            catalogs_title = [title.split('章 ', 1)[-1] for title in catalogs_title]
            d = {
                'book_id': book_id,
                'book_name': book_name,
                'book_url': url,
                'info': info,
                'intro': intro,
                'catalogs_L': L,
                # 'catalogs': catalogs,
                'catalogs_link': catalogs_link,
                'catalogs_title': catalogs_title
            }
            return d
        else:
            print('book_id: ', book_id, 'book_name:', book_name, '--------------------解析错误')
    else:
        print('book_id: ', book_id, '--------------------响应失败_', res.status_code)
    return None
# get_book_msg(6513)


def scan_books(book_id_begin, book_id_end):  # 左闭右开
    for book_id in range(book_id_begin, book_id_end, 1):
        try:
            d = get_book_msg(book_id)
            if d:
                with open("./books_msg/%s.json" % book_id, "w") as f:
                    dump(d, f)
                    print(book_id, '已保存')
            else:
                pass
        except Exception as e:
            print(format_exc(), e)
# scan_books(1, 10)


def load_book_msg(book_id):
    try:
        with open("./books_msg/%s.json" % book_id, "r") as f:
            return load(f)
    except Exception as e:
        print(format_exc(), e)
        return None
    pass


# test
def load_books_msg(book_id_begin, book_id_end):
    for book_id in range(book_id_begin, book_id_end, 1):
        print(load_book_msg(book_id))
# load_books_msg(1, 10)


def download_book(book_id):
    d = load_book_msg(book_id)
    catalogs_link = d.get('catalogs_link')
    catalogs_title = d.get('catalogs_title')
    pass








