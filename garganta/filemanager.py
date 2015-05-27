# -*- coding: utf-8 -*-
__author__ = 'Umut Karci'
import os

DOWNLOAD_PATH = os.path.expanduser("~/Downloads/Garganta")


def mkdir_p(path):
    import os
    import errno

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise exc


def _initialize():
    if os.path.exists(DOWNLOAD_PATH):
        if not os.path.isdir(DOWNLOAD_PATH):
            os.remove(DOWNLOAD_PATH)
            mkdir_p(DOWNLOAD_PATH)


def create_folder(manga_folder, episode_folder):
    _initialize()
    drc = os.path.join(DOWNLOAD_PATH, manga_folder, episode_folder)
    mkdir_p(drc)
    return drc
