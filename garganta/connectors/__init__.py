# -*- coding: utf-8 -*-
from garganta.settings import settings
from garganta.cache import NotCachedError


def get_connector(name):
    """
    :type name: str
    :rtype: AbstractBaseConnector
    """
    from garganta.connectors._mangatr import MangaTRConnector

    connectors = dict(map(lambda x: (x().get_name(), x()), [MangaTRConnector]))
    return connectors.get(name, None)


class Manga(object):
    def __init__(self, connector, name, url):
        self.connector = connector
        self.name = name
        self.url = url

    def serialize(self):
        return {
            "connector": self.connector.get_name(),
            "name": self.name,
            "url": self.url,
        }

    @staticmethod
    def deserialize(d):
        return Manga(
            get_connector(d["connector"]),
            d["name"],
            d["url"],
        )


class Episode(object):
    def __init__(self, manga, no, name, url):
        self.manga = manga
        self.no = no
        self.name = name
        self.url = url

    def serialize(self):
        return {
            "manga": self.manga.serialize(),
            "no": self.no,
            "name": self.name,
            "url": self.url,
        }

    @staticmethod
    def deserialize(d):
        return Episode(
            Manga.deserialize(d["manga"]),
            d["no"],
            d["name"],
            d["url"]
        )


class Page(object):
    def __init__(self, episode, no, url):
        self.episode = episode
        self.no = no
        self.url = url

    def serialize(self):
        return {
            "episode": self.episode.serialize(),
            "no": self.no,
            "url": self.url
        }

    @staticmethod
    def deserialize(d):
        return Page(
            Episode.deserialize(d["episode"]),
            d["no"],
            d["url"]
        )


import abc


class AbstractBaseConnector:
    __metaclass__ = abc.ABCMeta
    __instance = None

    def __new__(cls):
        """Override the __new__ method so that it is a singleton."""
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @abc.abstractmethod
    def get_name(self, ):
        """
        Returns name of the connector
        :rtype: unicode
        """
        return

    @abc.abstractmethod
    def manga_from_name(self, name):
        """
        Creates a manga object from it's name
        :type name: str
        :rtype: Manga
        """
        return

    @abc.abstractmethod
    def episode_from_no(self, manga_obj, no):
        """
        Creates an episode object from manga and no
        :type manga_obj: Manga
        :type no: int
        :rtype: Episode
        """
        return

    @abc.abstractmethod
    def get_manga_info(self, manga_obj):
        """
        Retrieve manga info from connector
        :type manga_obj: Manga
        :rtype: unicode
        """
        return

    @abc.abstractmethod
    def get_manga_list(self, ):
        """
        Retrieve manga list from connector
        :rtype: list[Manga]
        """
        return

    @abc.abstractmethod
    def get_episode_list(self, manga_obj):
        """
        Retrieve episode list from connector
        :type manga_obj: Manga
        :rtype: list[Episode]
        """
        return

    @abc.abstractmethod
    def get_page_list(self, episode_obj):
        """
        Retrieve page list from connector
        :type episode_obj: Episode
        :rtype: list[Page]
        """
        return


class AbstractCachedConnector(AbstractBaseConnector):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def _episode_from_no(self, manga_obj, no):
        return

    def episode_from_no(self, manga_obj, no):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_episode(
                    self.get_name(), manga_obj.name, no)
            except NotCachedError:
                pass

        try:
            episode_obj = self._episode_from_no(manga_obj, no)
        except ValueError:
            return None
        settings["cacheadapter"].save_episode(episode_obj)
        return episode_obj

    @abc.abstractmethod
    def _manga_from_name(self, name):
        return

    def manga_from_name(self, name):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_manga(
                    self.get_name(), name)
            except NotCachedError:
                pass
        manga_obj = self._manga_from_name(name)
        settings["cacheadapter"].save_manga(manga_obj)
        return manga_obj

    @abc.abstractmethod
    def _get_manga_info(self, manga_obj):
        return

    def get_manga_info(self, manga_obj):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_manga_info(
                    self.get_name(), manga_obj.name)
            except NotCachedError:
                pass

        info = self._get_manga_info(manga_obj)
        settings["cacheadapter"].save_manga_info(manga_obj, info)
        return info

    @abc.abstractmethod
    def _get_manga_list(self):
        return

    def get_manga_list(self):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_mangas(self.get_name())
            except NotCachedError:
                pass

        mangas = self._get_manga_list()
        settings["cacheadapter"].save_mangas(mangas)
        return mangas

    @abc.abstractmethod
    def _get_episode_list(self, manga_obj):
        return

    def get_episode_list(self, manga_obj):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_episodes(self.get_name(),
                                                              manga_obj.name)
            except NotCachedError:
                pass
        episodes = self._get_episode_list(manga_obj)
        settings["cacheadapter"].save_episodes(episodes)
        return episodes

    @abc.abstractmethod
    def _get_page_list(self, episode_obj):
        return

    def get_page_list(self, episode_obj):
        if settings["cachestatus"]:
            try:
                return settings["cacheadapter"].load_pages(
                    self.get_name(), episode_obj.manga.name, episode_obj.no)
            except NotCachedError:
                pass
        try:
            pages = self._get_page_list(episode_obj)
        except ValueError:
            return []
        settings["cacheadapter"].save_pages(pages)
        return pages
