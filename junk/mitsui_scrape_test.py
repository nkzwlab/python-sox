# -*- coding: utf-8 -*-
import pprint

# from bs4 import BeautifulSoup
import requests
import lxml.html
import chardet


def scrape(url):
    response = requests.get(url, headers={'Accept-Charset': 'UTF-8'})

    if response.status_code != 200:
        raise ValueError('status_code was bad: %s' % response.status_code)

    for k, v in response.headers.items():
        print '%s: %s' % (k, v)

    enc = chardet.detect(response.content)

    html = response.content.decode('utf-8')

    print '&&&&&& enc=%s' % enc

    # html = html.decode('utf-8')

    # html = html.decode('cp932')

    lines = html.split('\n')
    for line in lines:
        if 'charset' in line:
            print '@@@@ charset'
            print line
            print '@@@@ charset END'
        
    # print html
    return parse(html)

def parse(html):
    dom = lxml.html.fromstring(html)

    xpaths = [
        # ('state', "//DIV[@id='contents-bg03']/DIV/DIV[1]/DIV[1]/DIV/SPAN/IMG/@alt"),
        # ('address', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[1]/TD/SPAN"),
        # ('time', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[1]/SPAN"),
        # ('capacity', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[2]/SPAN"),
        # ('limit', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[3]/SPAN")

        # TBODY removed version
        ('state', "//DIV[@id='contents-bg03']/DIV/DIV[1]/DIV[1]/DIV/SPAN/IMG/@alt"),
        ('address', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[1]/TD/SPAN"),
        ('time', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[1]/SPAN"),
        ('capacity', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[2]/SPAN"),
        ('limit', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[3]/SPAN")
    ]

    print '----------'

    result = []

    for tdr_name, xpath in xpaths:
        xpath = xpath.lower()
        print '%s: %s' % (tdr_name, xpath)

        r = dom.body.xpath(xpath)
        print r

        if 0 < len(r):
            item = r[0]

            # if isinstance(item, (str, unicode)):
            #     result.append((tdr_name, item))
            # else:
            #     result.append((tdr_name, item.text))
            if not isinstance(item, (str, unicode)):
                item = item.text
            result.append((tdr_name, item))

    return result


def main():
    url = 'http://www.repark.jp/parking_user/time/result/detail/?park=REP0005186'


    # f = '/Users/tomotaka/Desktop/mitsui_sample.html'
    # html = open(f, 'rb').read()

    result = scrape(url)
    # result = parse(html)
    print '--------'
    # pprint.pprint(result)
    for key, item in result:
        print '%s: %s' % (key, item)


if __name__ == '__main__':
    main()
