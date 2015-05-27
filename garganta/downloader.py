# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'Umut Karci'

from collections import deque
from wget import download
from multiprocessing.pool import ThreadPool
from threading import current_thread
from functools import partial

download_list = deque()
pool = ThreadPool(3)
pool_running = False

bar_dict = {}
prev_line_len = 0


def general_bar(current, total, _=None, name=None, thread=None):
    global bar_dict, prev_line_len
    bar_dict[thread] = name, current, total
    bar = "".join(map(lambda x:
                      "[{file} {current}KiB/{total}KiB({percent}%)]".format(
                          file=x[0], current=x[1] / 1024, total=x[2] / 1024,
                          percent=x[1] * 100 / x[2]),
                      bar_dict.values()))
    print(bar, end="")
    print("\r" * prev_line_len, end="")
    print(" " * prev_line_len, end="")
    prev_line_len = len(bar)


def download_worker(q):
    url, path = q
    br = partial(general_bar, name=url.split("/")[-1], thread=current_thread())
    download(url, path, br)


def stop_download():
    global pool_running
    pool.join()
    pool_running = False


def start_download():
    global pool_running
    pool_running = True
    pool.imap(download_worker, download_list)
    pool_running = False
