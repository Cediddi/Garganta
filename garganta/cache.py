# -*- coding: utf-8 -*-

import os
import json
from glob import glob
from shutil import rmtree

from garganta.utils import check_folder, list_folders, slugify


class NotCachedError(Exception):
    pass


# noinspection PyClassHasNoInit
class FileCache:
    @staticmethod
    def invalidate(connector):
        from garganta.settings import settings

        rmtree(os.path.join(settings["cachedir"], connector))

    @staticmethod
    def load_mangas(connector):
        from garganta.settings import settings

        connector_dir = os.path.join(settings["cachedir"],
                                     connector)
        if not check_folder(connector_dir):
            raise NotCachedError

        manga_names = list_folders(connector_dir)
        mangas = []
        for manga_name in manga_names:
            manga = FileCache.load_manga(connector, manga_name)
            mangas.append(manga)

        if not len(mangas):
            raise NotCachedError

        return mangas

    @staticmethod
    def save_mangas(manga_obj_list):
        for manga_obj in manga_obj_list:
            FileCache.save_manga(manga_obj)

    @staticmethod
    def save_manga(manga_obj):
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 manga_obj.connector.get_name(),
                                 slugify(manga_obj.name))
        check_folder(manga_dir)

        manga_file = os.path.join(manga_dir, "obj.json")
        with open(manga_file, "w") as f:
            json.dump(manga_obj.serialize(), f)

    @staticmethod
    def load_manga(connector, manga_name):
        from garganta.connectors import Manga
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 connector,
                                 slugify(manga_name))

        if check_folder(manga_dir):
            manga_file = os.path.join(manga_dir, "obj.json")
            if os.path.exists(manga_file) and os.path.isfile(manga_file):
                with open(manga_file) as f:
                    try:
                        return Manga.deserialize(json.loads(f.read()))
                    except ValueError:
                        pass
        rmtree(manga_dir)
        raise NotCachedError

    @staticmethod
    def save_manga_info(manga_obj, info):
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 manga_obj.connector.get_name(),
                                 slugify(manga_obj.name))
        check_folder(manga_dir)

        manga_file = os.path.join(manga_dir, "info.json")
        with open(manga_file, "w") as f:
            json.dump(info, f)

    @staticmethod
    def load_manga_info(connector, manga_name):
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 connector,
                                 slugify(manga_name))

        if check_folder(manga_dir):
            info_file = os.path.join(manga_dir, "info.json")
            if os.path.exists(info_file) and os.path.isfile(info_file):
                with open(info_file) as f:
                    try:
                        return json.load(f)
                    except ValueError:
                        pass
            rmtree(info_file)
        raise NotCachedError

    @staticmethod
    def load_episodes(connector, manga_name):
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 connector,
                                 slugify(manga_name))

        if not check_folder(manga_dir):
            raise NotCachedError

        episode_nos = list_folders(manga_dir)
        episodes = []
        for episode_no in episode_nos:
            episode = FileCache.load_episode(
                connector, manga_name, int(episode_no))
            episodes.append(episode)

        if not len(episodes):
            raise NotCachedError

        return episodes

    @staticmethod
    def save_episodes(episode_obj_list):
        for episode_obj in episode_obj_list:
            FileCache.save_episode(episode_obj)

    @staticmethod
    def save_episode(episode_obj):
        from garganta.settings import settings

        episode_dir = os.path.join(settings["cachedir"],
                                   episode_obj.manga.connector.get_name(),
                                   slugify(episode_obj.manga.name),
                                   str(episode_obj.no))
        check_folder(episode_dir)

        episode_file = os.path.join(episode_dir, "obj.json")
        with open(episode_file, "w") as f:
            json.dump(episode_obj.serialize(), f)

    @staticmethod
    def load_episode(connector, manga_name, episode_no):
        from garganta.connectors import Episode
        from garganta.settings import settings

        episode_dir = os.path.join(settings["cachedir"],
                                   connector,
                                   slugify(manga_name),
                                   str(episode_no))

        if check_folder(episode_dir):
            episode_file = os.path.join(episode_dir, "obj.json")
            if os.path.exists(episode_file) and os.path.isfile(episode_file):
                with open(episode_file) as f:
                    try:
                        return Episode.deserialize(json.load(f))
                    except ValueError:
                        pass
        rmtree(episode_dir)
        raise NotCachedError

    @staticmethod
    def load_pages(connector, manga_name, episode_no):
        from garganta.settings import settings

        manga_dir = os.path.join(settings["cachedir"],
                                 connector,
                                 slugify(manga_name),
                                 str(episode_no))

        if not check_folder(manga_dir):
            raise NotCachedError

        page_nos = glob(manga_dir + "/*.json")
        page_nos = map(
            lambda x: x.replace(manga_dir + "/", "").replace(".json", ""),
            page_nos)

        pages = []
        for page_no in page_nos:
            if page_no.isdigit():
                page = FileCache.load_page(
                    connector, manga_name, int(episode_no),
                    int(page_no.replace(".json", "")))
                pages.append(page)
            else:
                pass
        if not len(pages):
            raise NotCachedError

        return pages

    @staticmethod
    def save_pages(page_obj_list):
        for page_obj in page_obj_list:
            FileCache.save_page(page_obj)

    @staticmethod
    def save_page(page_obj):
        from garganta.settings import settings

        episode_dir = os.path.join(settings["cachedir"],
                                   page_obj.episode.manga.connector.get_name(),
                                   slugify(page_obj.episode.manga.name),
                                   str(page_obj.episode.no))
        check_folder(episode_dir)

        page_file = os.path.join(episode_dir, str(page_obj.no) + ".json")
        with open(page_file, "w") as f:
            json.dump(page_obj.serialize(), f)

    @staticmethod
    def load_page(connector, manga_name, episode_no, page_no):
        from garganta.connectors import Page
        from garganta.settings import settings

        episode_dir = os.path.join(settings["cachedir"],
                                   connector,
                                   slugify(manga_name),
                                   str(episode_no))

        if check_folder(episode_dir):
            page_file = os.path.join(episode_dir, str(page_no) + ".json")
            if os.path.exists(page_file) and os.path.isfile(page_file):
                with open(page_file) as f:
                    try:
                        return Page.deserialize(json.load(f))
                    except ValueError:
                        pass
            rmtree(page_file)
        raise NotCachedError
