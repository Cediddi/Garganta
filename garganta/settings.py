# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
from collections import deque

import appdirs

from .utils import general_bar


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # noinspection PyArgumentList
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


# Python2
class Settings(object):
    __metaclass__ = Singleton

    def __init__(self, **defaults):
        self._data = defaults
        self.load()

    def __setitem__(self, key, value):
        self._data[key] = value
        return value

    def __getitem__(self, item):
        return self._data[item]

    def load(self):
        from garganta.utils import mkdir_p

        conf_folder = self["configdir"]
        conf_file = os.path.join(self["configdir"], "conf.json")
        if not os.path.exists(conf_folder):
            mkdir_p(conf_folder)
            self.save()

        if not os.path.exists(conf_file):
            self.save()

        with open(conf_file) as f:
            try:
                conf_data = json.load(f)
            except ValueError:
                os.remove(conf_file)
                self.save()
                conf_data = {}

        self.update(conf_data)

    def save(self):
        from garganta.utils import mkdir_p

        conf_folder = self["configdir"]
        conf_file = os.path.join(self["configdir"], "conf.json")
        if not os.path.exists(conf_folder):
            mkdir_p(conf_folder)

        with open(conf_file, "w") as f:
            json.dump(self._data, f, indent=2, separators=(',', ': '))

    def update(self, dictionary):
        for key, value in dictionary.items():
            self[key] = value

    def items(self):
        return self._data.items()


from garganta.cache import FileCache

settings = Settings(poolsize=3,
                    downloadbar=general_bar,
                    downloadpath=os.path.expanduser("~/Downloads/Garganta"),
                    defaultconnector="manga-tr",
                    configdir=appdirs.user_config_dir("Garganta", "Cediddi"),
                    cachedir=appdirs.user_cache_dir("Garganta", "Cediddi"),
                    adapters=["manga-tr"],
                    done=0,
                    queue=deque(),
                    cachestatus=False,
                    cacheadapter=FileCache)
