# -*- coding: utf-8 -*-
from __future__ import print_function

from multiprocessing.pool import ThreadPool
from threading import current_thread
from functools import partial
import os
from urllib.request import urlretrieve

from garganta.settings import settings
from garganta.utils import fix_type

pool = ThreadPool(settings["poolsize"])


def download_worker(q):
    page, path = q
    filename = page.url.split("/")[-1]
    file_full_path = os.path.join(path, filename)
    br = partial(settings["downloadbar"],
                 name=filename,
                 thread=current_thread())
    saved, _ = urlretrieve(page.url, file_full_path, br)
    fix_type(saved)
    settings["done"] += 1


def stop_download():
    pool.join()


def start_download(async=False, callback=None):
    def _callback(*args, **kwargs):
        settings["queue"].clear()
        settings["done"] = 0
        if callback is not None:
            return callback(*args, **kwargs)
        else:
            return None

    results = pool.map_async(download_worker,
                             settings["queue"],
                             callback=_callback)
    if not async:
        results.get()
        settings["queue"].clear()
        settings["done"] = 0
