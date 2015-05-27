# -*- coding: utf-8 -*-
__author__ = 'Umut Karci'
import importlib


def get_adapter(name):
    if name in ["manga-tr", ]:
        module = importlib.import_module("garganta.sites." + name)
        return module
