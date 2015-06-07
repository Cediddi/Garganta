# -*- coding: utf-8 -*-

from time import time
from urllib import request, parse
import re

from bs4 import BeautifulSoup
from slugify import Slugify

from garganta.connectors import Manga, Episode, Page, AbstractCachedConnector
from garganta.utils import ireplace


class MangaTRConnector(AbstractCachedConnector):
    def __init__(self):
        from http import cookiejar

        super().__init__()
        self.base_url = "http://www.manga-tr.com/"
        jar = cookiejar.LWPCookieJar()
        jar.set_cookie(
            cookiejar.Cookie(0, "read_type", "1",
                             None, False,
                             'www.manga-tr.com', False, False,
                             "/", False,
                             False,
                             time() + 157784630, False,
                             None, None, {})
        )
        self.req = request.build_opener(request.HTTPCookieProcessor(jar))
        self.slugify = Slugify(safe_chars=".")
        self.manga_re = re.compile(r"^manga-[\w\-\.]+\.html$")
        self.episode_re = re.compile(r"^read[\w\-\.]+\.html$")

    def j_url(self, url):
        return parse.urljoin(self.base_url, url)

    def get_name(self):
        """
        Returns name of the connector
        :rtype: unicode
        """
        return "manga-tr"

    def _manga_from_name(self, name):
        """
        Creates a manga object from it's name
        :type name: str
        :rtype: Manga
        """
        url = self.j_url("manga-{}.html".format(self.slugify(name.lower())))
        return Manga(self, name, url)

    def _episode_from_no(self, manga_obj, no):
        """
        Creates an episode object from manga and no
        :type manga_obj: Manga
        :type no: int
        :rtype: Episode
        """
        url = self.j_url("read-{name}-chapter-{no}.html".format(
            name=self.slugify(manga_obj.name), no=no))

        response = self.req.open(url)
        if response.geturl() == 'http://www.manga-tr.com/index.html':
            raise ValueError("Missing Episode")
        soup = BeautifulSoup(response.read())
        meta = soup.find_all("meta",
                             attrs={"name": "description"})[0]["content"]
        name = meta.split(",")[2].strip()
        return Episode(manga_obj, no, name, url)

    def _get_manga_info(self, manga_obj):
        """
        Retrieve manga info from connector
        :type manga_obj: Manga
        :rtype: unicode
        """
        response = self.req.open(manga_obj.url)
        soup = BeautifulSoup(response.read())
        # What returns is a bit hacky.
        return soup.find_all("div", attrs={"class": "well"})[0].p.string

    def _get_manga_list(self):
        """
        Retrieve manga list from connector
        :rtype: list[Manga]
        """
        response = self.req.open(self.j_url("manga-list.html"))
        soup = BeautifulSoup(response.read())
        tags = soup.find_all("a", attrs={"href": self.manga_re})
        tags.pop(0)  # pass "Hepsi" link
        return [Manga(self, t.text, self.j_url(t.attrs["href"])) for t in tags]

    def _get_episode_list(self, manga_obj):
        """
        Retrieve episode list from connector
        :type manga_obj: Manga
        :rtype: list[Episode]
        """
        response = self.req.open(manga_obj.url)
        soup = BeautifulSoup(response.read())
        tags = soup.find_all("a", attrs={"href": self.episode_re})
        rlist = []
        for t in tags:
            temp = ireplace(manga_obj.name, "", t.text).strip()
            if "-" in temp:
                no = int(temp[:temp.index("-") - 1])  # There should be dash
                name = temp[temp.index("-") + 2:]  # Best solution is slicing
            else:
                no = int(temp)
                name = "-"
            rlist.append(
                Episode(manga_obj, no, name, self.j_url(t.attrs["href"])))
        return rlist

    def _get_page_list(self, episode_obj):
        """
        Retrieve page list from connector
        :type episode_obj: Episode
        :rtype: list[Page]
        """
        response = self.req.open(episode_obj.url)
        if response.geturl() == 'http://www.manga-tr.com/index.html':
            raise ValueError("Missing Episode")
        soup = BeautifulSoup(response.read())
        img_tags = soup.find_all("img", attrs={"class": "chapter-img"})
        urls = map(lambda x: self.j_url(x["src"]), img_tags)
        return [Page(episode_obj, idx + 1, url) for idx, url in
                enumerate(urls)]
