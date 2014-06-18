#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent


def hello(i):
    t = (5 - i)
    gevent.sleep(t)
    print 'hello %d' % i


def main():
    threads = set([])

    for i in range(3):
        t = gevent.spawn(hello, i)
        t.number = i
        threads.add(t)

    while 0 < len(threads):
        got = gevent.wait(threads, count=1)
        t = got[0]
        threads.remove(t)
        print 'finished: %d' % t.number

    print 'ALL FINISH'


if __name__ == '__main__':
    gevent.spawn(main).join()
