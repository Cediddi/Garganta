# -*- coding: utf-8 -*-
__author__ = 'Umut Karci'

import mechanize
from bs4 import BeautifulSoup
import cookielib
from time import time
from slugify import Slugify
from collections import OrderedDict as dict

br = mechanize.Browser()

cookiejar = cookielib.LWPCookieJar()
br.set_cookiejar(cookiejar)

cookie = cookielib.Cookie(0, "read_type", "1",
                          None, False,
                          'www.manga-tr.com', False, False,
                          "/", False,
                          False,
                          time() + 157784630, False,
                          None, None, {})
cookiejar.set_cookie(cookie)

slugify = Slugify(safe_chars=".")


def list_mangas():
    br.open("http://www.manga-tr.com/manga-list.html")
    mangas = br.links(url_regex=r"^manga-[\w\-\.]+\.html$")
    mangas.next()  # Ignore "hepsi" link
    return dict([(link.text, link) for link in mangas])


def manga_url_from_name(name):
    return "http://www.manga-tr.com/manga-" + name + ".html"


def list_episodes(link=None, url=None, name=None):
    if link:
        br.follow_link(link)
    elif url:
        br.open(url)
    elif name:
        name = slugify(name)
        br.open(manga_url_from_name(name))
    else:
        raise ValueError("Either link, url or name argument should be given.")
    return dict(reversed([(link.text, link) for link in
                          br.links(url_regex=r"^read[\w\-\.]+\.html$")]))


def manga_info(link=None, url=None, name=None):
    if link:
        br.follow_link(link)
    elif url:
        br.open(url)
    elif name:
        name = slugify(name)
        br.open(manga_url_from_name(name))
    else:
        raise ValueError("Either link, url or name argument should be given.")
    soup = BeautifulSoup(br.response().read())
    return soup.find_all("div", attrs={"class": "well"})[0].p.string  # HACK


def episode_url_from_episode_no(name, no):
    return "http://www.manga-tr.com/read-{name}-chapter-{no}.html".format(
        name=name, no=no)


def get_pages(link=None, url=None, name=None, no=None):
    if link:
        br.follow_link(link)
    elif url:
        br.open(url)
    elif name and no:
        name = slugify(name)
        br.open(episode_url_from_episode_no(name, no))
    else:
        raise ValueError(
            "Either link, url or name and id arguments should be given.")

    soup = BeautifulSoup(br.response().read())

    if not (name and no):
        name = soup.find("a", class_="navbar-brand").string
        no = soup.find("title").string.split(",")[0].replace(name, "").strip()

    e_name = soup.find_all("meta", attrs={"name": "description"})[0]["content"]
    e_name = e_name[e_name.find(str(no)) + len(str(no)) + 2:]
    img_tags = soup.find_all("img", attrs={"class": "chapter-img"})
    return name, no, e_name, map(
        lambda x: "http://www.manga-tr.com/" + x["src"], img_tags)
