# -*- coding: utf-8 -*-
from threading import RLock
import shutil

from slugify import Slugify

slugify = Slugify(to_lower=True)


def fix_type(f):
    """Some files have wrong extensions. eg. Gintama 411 from manga-tr has
    png files but their extensions are .jpg, thus we need to rename them in
    order to make this program crossplatform ready."""
    from imghdr import what
    from os.path import splitext
    from shutil import move

    real = what(f)
    current = splitext(f)[1].replace(".", "")

    move(f, f.replace(current, real))


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


def create_folder(episode_obj):
    import os
    from garganta.settings import settings

    drc = os.path.join(settings["downloadpath"],
                       slugify(episode_obj.manga.name),
                       "#{no}-{name}".format(no=episode_obj.no,
                                             name=slugify(episode_obj.name)))
    mkdir_p(drc)
    return drc


def check_folder(folder):
    import os

    if not os.path.exists(folder):
        mkdir_p(folder)
        return False
    return True


def list_folders(folder):
    import os

    drs = []
    for dr in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, dr)):
            drs.append(dr)

    return drs


bar_dict = {}
prev_line_len = 0
done_downloads = 0
bar_lock = RLock()


def general_bar(blocks, block_size, total_size, name=None, thread=None):
    global bar_dict, prev_line_len, bar_lock
    from garganta.settings import settings

    if blocks * block_size < total_size:
        current = blocks * block_size
    else:
        current = total_size

    with bar_lock:
        bar_dict[thread] = name, current, total_size

        total_s = 0
        q_str = " Q = {}".format(len(settings["queue"]) - settings["done"])
        col_size = shutil.get_terminal_size().columns
        for _, values in bar_dict.items():

            s = u"[{file} {current}KiB/{total}KiB({percent:.2f}%)]".format(
                file=values[0],
                current=int(values[1] / 1024),
                total=int(values[2] / 1024),
                percent=values[1] * 100 / values[2])

            if total_s + len(s) < col_size - len(q_str):
                print(s, end="")
                total_s += len(s)

        print(q_str, end="")
        total_s += len(q_str)

        if prev_line_len > total_s:
            spaces = " " * (prev_line_len - total_s)
            print(spaces, end="", flush=True)
            total_s += len(spaces)

        print("\r" * total_s, end="", flush=True)
        prev_line_len = total_s


def ireplace(old, new, text):
    """
    Replace case insensitive
    Raises ValueError if string not found
    """
    index_l = text.lower().index(old.lower())
    return text[:index_l] + new + text[index_l + len(old):]
