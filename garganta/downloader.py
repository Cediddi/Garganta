# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'Umut Karci'

from collections import deque
from wget import download
from multiprocessing.pool import ThreadPool
from threading import current_thread
from functools import partial

download_list = deque()
done_downloads = 0
pool = ThreadPool(3)

bar_dict = {}
prev_line_len = 0


def general_bar(current, total, _=None, name=None, thread=None):
    global bar_dict, prev_line_len, done_downloads
    bar_dict[thread] = name, current, total
    bar = u"".join(map(lambda x:
                      u"[{file} {current}KiB/{total}KiB({percent}%)]".format(
                          file=x[0], current=x[1] / 1024, total=x[2] / 1024,
                          percent=x[1] * 100 / x[2]),
                      bar_dict.values()))
    bar += " Queue = {}".format(len(download_list) - done_downloads)
    print("\r" * prev_line_len, end="")
    line_len = len(bar)
    if prev_line_len > len(bar):
        bar += " " * (prev_line_len - len(bar))
    print(bar, end="")
    prev_line_len = line_len


def download_worker(q):
    global done_downloads
    url, path = q
    br = partial(general_bar, name=url.split("/")[-1], thread=current_thread())
    download(url, path, br)
    done_downloads += 1


def stop_download():
    pool.join()


def start_download():
    pool.map(download_worker, download_list)
