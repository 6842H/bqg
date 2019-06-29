# coding: utf-8 
# @Time : 2019/6/29 上午 11:18 
# @Author : gyn 
# @email : guogyn@foxmail.com

# 88588
from math import ceil
from lxml import etree
from requests import get
from re import compile, findall
from random import choice
from traceback import format_exc
from DBPool import DBPool
from threading import Thread
import warnings
warnings.filterwarnings('ignore')


url0 = "https://www.xbiquge6.com/"
pattern_for_chapter_link_id = compile('/(\d*?)\.')
books_cols = ['book_id', 'book_name', 'author', 'state', 'update_time', 'intro']
chapters_cols = ['chapter_id', 'book_id', 'title', 'state', 'content']
pause_time = 120    # 连续发生多次异常时休眠时间

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
    url = url0 + get_real_book_id(book_id)
    res = mget(url)
    if res.status_code == 200:
        html = etree.HTML(res.content)
        info = html.xpath('//div[@id="info"]')[0]
        book_name = info.xpath('.//h1/text()')[0].strip()
        temp = info.xpath('./p/text()')
        temp.remove(',')
        # print(temp)
        author = temp[0].split('：')[-1].strip()
        state = temp[1].split('：')[-1].strip()
        update_time = temp[2].split('：')[-1].strip()
        intro = html.xpath('string(//div[@id="intro"])').strip().split('各位书友')[0] or '暂无'   # 小说内容
        DBPool.insert_item(table_name='books', cols_tuple=books_cols, values_tuple=(book_id, book_name, author, state, update_time, intro))
        # return
        div_list = html.xpath('//div[@id="list"]')[0]
        chapters_link = div_list.xpath('.//dd//a/@href')    # 章节链接
        chapters_title = div_list.xpath('.//dd//a/text()')  # 章节标题
        L = len(chapters_link)
        if L == len(chapters_title):
            d = [
                [findall(pattern_for_chapter_link_id, link)[0], book_id, title.split(' ', 1)[-1], 0, '']
                for link, title in zip(chapters_link, chapters_title)
                ]
            DBPool.insert_item(table_name='chapters', cols_tuple=chapters_cols, values_tuple=d)
        else:
            print('book_id: ', book_id, 'book_name:', book_name, '--------------------解析错误')
    else:
        print('book_id: ', book_id, '--------------------响应失败_', res.status_code)
# get_book_msg(6513)


# 收录书籍信息和章节
def scan_books(book_id_begin, book_id_end):  # 左闭右开
    for book_id in range(book_id_begin, book_id_end, 1):
        get_book_msg(book_id)
# scan_books(1, 10)


def scan_books_in_thread(book_id_begin, book_id_end, thread_n):
    step = ceil((book_id_end-book_id_begin) / thread_n)
    threads = []
    for i in range(thread_n - 1):
        threads.append(Thread(name=str(i), target=scan_books, args=(book_id_begin, book_id_begin+step)))
        book_id_begin += step
    threads.append(Thread(name=str(i), target=scan_books, args=(book_id_begin, book_id_end)))
    for t in threads:
        t.start()


# 下载一个章节
def download_chapter(book_id=6513, chapter_id=1443774):
    url = url0 + get_real_book_id(book_id) + '/' + str(chapter_id) + '.html'
    res = mget(url)
    if res.status_code == 200:
        html = etree.HTML(res.content)
        content = html.xpath('string(//div[@id="content"])')
        # print(content)
        content = content.strip().replace("'", "''")
        sql = "update chapters set state=1, content='%s' where chapter_id=%s " % (content, chapter_id)
        try:
            DBPool.exe_sql(sql)
            print('book_id: ', book_id, 'chapter_id', chapter_id, '已保存')
        except Exception as e:
            print('book_id: ', book_id, 'chapter_id', chapter_id, '--------------------content保存失败')
            print(format_exc(), e)
    else:
        print('book_id: ', book_id, 'chapter_id', chapter_id, '--------------------响应失败_', res.status_code)
# download_chapter()


# 下载n个章节, 不分小说，只下章节
def download_chapters(chapters_n=100):
    sql = "select chapter_id, book_id from chapters where state=0 limit %d" % chapters_n
    res = DBPool.exe_sql(sql)  # 二维tuple
    if res:
        for item in res:
            try:
                download_chapter(item[1], item[0])
            except Exception as e:
                print(format_exc(), e)
# download_chapters(20)


# 下载整本书
def download_book(book_id=6513):
    sql = "select chapter_id from chapters where book_id=%d and state=0" % book_id
    res = DBPool.exe_sql(sql)     # 二维tuple
    if res:
        for item in res:
            try:
                download_chapter(book_id, item[0])
            except Exception as e:
                print(format_exc(), e)
# download_book()


def download_book_cell(book_id, chapters):
    for chapter in chapters:
        try:
            download_chapter(book_id, chapter[0])
        except Exception as e:
            print(format_exc(), e)


# 下载整本书
def download_book_in_thread(book_id=6513, thread_n=5):
    sql = "select chapter_id from chapters where book_id=%d and state=0" % book_id
    res = DBPool.exe_sql(sql)     # 二维tuple
    if res:
        L = len(res)
        step = ceil(L / thread_n)
        threads = []
        for i in range(thread_n):
            threads.append(Thread(name=str(i), target=download_book_cell, args=(book_id, res[i * step: (i + 1) * step])))
        for t in threads:
            t.start()

# download_book()


# 下载给定的任务包
def download_chapter_cell(chapter_book):
    if chapter_book:
        for item in chapter_book:
            try:
                download_chapter(book_id=item[1], chapter_id=item[0])
            except Exception as e:
                print(format_exc(), e)


# 开线程下载
def download_chapters_in_thread(chapters_n=100, thread_n=5):
    sql = "select chapter_id, book_id from chapters where state=0 limit %d" % chapters_n
    res = DBPool.exe_sql(sql)  # 二维tuple
    if res:
        step = ceil(chapters_n / thread_n)
        threads = []
        for i in range(thread_n):
            threads.append(Thread(name=str(i), target=download_chapter_cell, args=(res[i*step: (i+1)*step],)))
        for t in threads:
            t.start()


# scan_books_in_thread(1, 1000, 10)
# download_chapters_in_thread(10000, 10)
# download_book_in_thread(24, 10)











