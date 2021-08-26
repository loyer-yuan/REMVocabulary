from MySQLConn import MyPymysql
import urllib.request
from lxml import etree
import re
import time
from functools import reduce

debug = False


# 获得页面数据
def get_page(myword):
    basurl = 'http://cn.bing.com/dict/search?q='
    searchurl = basurl + myword
    response = urllib.request.urlopen(searchurl)
    html = response.read()
    return html


# 获得单词释义
def get_chitiao(html_selector):
    chitiao = {}
    hanyi_xpath = '/html/body/div[1]/div/div/div[1]/div[1]/ul/li'
    get_hanyi = html_selector.xpath(hanyi_xpath)
    for item in get_hanyi:
        it = item.xpath('span')
        chitiao[it[0].text] = it[1].xpath('span')[0].text
    if debug:
        for key, value in chitiao.items():
            print('key: ', key, 'value: ', value)
    return chitiao


# 获得单词音标和读音连接
def get_yinbiao(html_selector):
    yinbiao = {}
    yingbiao_xpath = '/html/body/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div'
    bbb = "(https\:.*?mp3)"
    reobj1 = re.compile(bbb, re.I | re.M | re.S)
    get_yingbiao = html_selector.xpath(yingbiao_xpath)
    for item in get_yingbiao:
        it = item.xpath('div')
        if len(it) > 0:
            if len(it) > 1 and len(it[1].xpath('a')) > 0:
                ddd = reobj1.findall(it[1].xpath('a')[0].get('onmouseover', None))
                yinbiao[it[0].text] = ddd[0]
            else:
                yinbiao[it[0].text] = None
            if len(it) > 3 and len(it[3].xpath('a')) > 0:
                ddd = reobj1.findall(it[3].xpath('a')[0].get('onmouseover', None))
                yinbiao[it[2].text] = ddd[0]
            elif len(it) > 2:
                yinbiao[it[2].text] = None
    if debug:
        for key, value in yinbiao.items():
            print('key: ', key, 'value: ', value)
    return yinbiao


# 获得例句
def get_liju(html_selector):
    liju = {}
    get_liju_e = html_selector.xpath('//*[@class="val_ex"]')
    get_liju_cn = html_selector.xpath('//*[@class="bil_ex"]')
    get_len = len(get_liju_e)
    for i in range(get_len):
        liju[get_liju_e[i].text] = get_liju_cn[i].text
    if debug:
        for key, value in liju.items():
            print('key: ', key, 'value: ', value)
    return liju


def get_word(word):
    # 获得页面
    pagehtml = get_page(word)
    selector = etree.HTML(pagehtml.decode('utf-8'))
    # 单词释义
    chitiao = get_chitiao(selector)
    # 单词音标及读音
    yinbiao = get_yinbiao(selector)
    # 例句
    liju = get_liju(selector)
    words = {'word': word,
             'yinbiao': yinbiao,
             'chitiao': chitiao,
             'liju': liju}
    return words


if __name__ == '__main__':
    # 使用连接池管理链接
    count = 0
    error = 0
    mysql = MyPymysql()
    key = False
    sql = 'select word from enwords;'
    # 获取外面单词库的单词
    wordList = mysql.getAll(sql)
    # 插入的sql语句
    sql_vocabulary = 'insert into vocabulary(words, part_of_speech, chinese) values ' \
                     '(%s, %s, %s);'
    sql_example = 'insert into example(example, words, chinese)' \
                  'values (%s, %s, %s);'
    sql_pronounce = 'insert into pronounce(words, pronounce, url)' \
                    'values (%s, %s, %s);'
    # 一个单词一个单词插入
    for w in wordList:
        w = w[0]
        print("执行查找 " + w)
        if mysql.getOne('select 1 from vocabulary where words = %s', w):
            count += 1
            print("数据库已有"+w+"，跳过该单词")
            continue
        # 遍历之前的已经存在在数据库中的数据不需要sleep
        if key:
            time.sleep(0.05)
        result = get_word(w)
        # 插入所有词性和词意，这是最基础，只有存在，才能插入发音和例句
        if result['chitiao']:
            key = True  # 需要sleep，防止屏蔽
            print("开始插入 " + w)
            # 开始事务
            try:
                mysql.begin()
                tempList = []
                for x, y in result['chitiao'].items():
                    tempList.append([w, x, y])
                mysql.insertMany(sql_vocabulary, tempList)
                # 插入所有例句
                if result['liju']:
                    tempList = []
                    for x, y in result['liju'].items():
                        tempList.append([x, w, y])
                    mysql.insertMany(sql_example, tempList)
                # 插入音标和读音的url
                if result['yinbiao']:
                    tempList = []
                    for x, y in result['yinbiao'].items():
                        tempList.append([w, x, y])
                    mysql.insertMany(sql_pronounce, tempList)
                mysql.end()
                count += 1
            except:
                error += 1
                mysql.end(option='0')
            print("结束插入 " + w + "\t录入：" + str(count) + "\t错误：" + str(error) + "\t进度为： " + str((count + error) / 103976 * 100) + "%")
        else:
            error += 1
            print("找不到单词" + w + "\t录入：" + str(count) + "\t错误：" + str(error) + "\t进度为： " + str((count + error) / 103976 * 100) + "%")
    mysql.dispose()
    print("Finish fulfill the db of vocabulary")
