# -*- coding: utf-8 -*-
__author__ = 'Umut Karci'

import json
import os
from argparse import ArgumentParser

from appdirs import user_config_dir, user_cache_dir

import downloader
import filemanager
import scrapper
from filemanager import mkdir_p
def load_conf():
    if os.path.exists(config_file):
        try:
            with file(config_file) as f:
                return json.load(f)
        except ValueError:
            os.remove(config_file)
            with file(config_file, "w") as f:
                json.dump(conf, f)
    else:
        with file(config_file, "w") as f:
            json.dump(conf, f)

    return {}


def download_episode(m, *es):
    downloader.DOWNLOAD_PATH = conf["download_dir"]
    for e in es:
        manga, episode, title, pages = adapter.get_pages(name=m, no=e)
        folder = filemanager.create_folder(manga, u"{e} - {en}".format(
            e=episode, en=title))

        print u"{m} - #{e} {t} added to download queue".format(
            m=manga, e=episode, t=title)
        for page in pages:
            downloader.download_list.append((page, folder))

    downloader.start_download()


def init_parser():
    arg_parser = ArgumentParser("Garganta")

    arg_parser.add_argument("-s", "--site",
                            action='store', default=conf["site"],
                            choices=["manga-tr", "mangaturk"],
                            help="Site you want to use, Default: manga-tr")

    arg_parser.add_argument("-l", "--list",
                            action='store_true',
                            help="if called alone, lists all mangas,\n"
                                 "if called with --manga lists all episodes\n"
                                 "if called with --episode counts pages")

    arg_parser.add_argument("-m", "--manga",
                            action='store', nargs="+",
                            help="The manga you want.")

    arg_parser.add_argument("-e", "--episode",
                            action='store', type=int, nargs="+",
                            help="The episode you want to download")

    arg_parser.add_argument("-d", "--download-path", action='store',
                            default=conf["download_dir"],
                            help="Download path you want to use")

    arg_parser.add_argument("-f", "--force", action='store_true',
                            help="Ignores local caches")

    return vars(arg_parser.parse_args()), arg_parser


confdir = user_config_dir("Garganta", "Cediddi")
if not os.path.exists(confdir):
    mkdir_p(confdir)

config_file = os.path.join(confdir, "conf.json")

conf = {"site": "manga-tr",
        "download_dir": os.path.expanduser("~/Downloads/Garganta")}
conf.update(load_conf())

cachedir = user_cache_dir("Garganta", "Cediddi")
if not os.path.exists(cachedir):
    mkdir_p(cachedir)


args, parser = init_parser()
adapter = scrapper.get_adapter(args["site"])
args["manga"] = " ".join(args["manga"]) if args["manga"] is not None else None


def main():
    if args["list"]:
        if args["manga"] is not None:
            if args["episode"] is not None:
                for ep in args["episode"]:
                    manga, episode, title, pages = adapter.get_pages(
                        name=args["manga"], no=ep)
                    print u"{p} pages found on {m} - #{e} {t}".format(
                        p=len(pages), m=manga, e=episode, t=title)
            else:
                cachefile = os.path.join(
                    cachedir, u"{s}_{m}_episodes.json".format(
                        s=adapter.slugify(args["site"]),
                        m=adapter.slugify(args["manga"])))
                if os.path.exists(cachefile) and args["force"] is False:
                    try:
                        eps = json.load(file(cachefile))
                    except ValueError:
                        os.remove(cachefile)
                        eps = adapter.list_episodes(name=args["manga"]).keys()
                        json.dump(eps, file(cachefile, "w"))
                else:
                    eps = adapter.list_episodes(name=args["manga"]).keys()
                    json.dump(eps, file(cachefile, "w"))

                for ep in eps:
                    print ep
        else:
            cachefile = os.path.join(cachedir, u"{s}_mangas.json".format(
                s=adapter.slugify(args["site"])))
            if os.path.exists(cachefile) and args["force"] is False:
                try:
                    mangas = json.load(file(cachefile))
                except ValueError:
                    os.remove(cachefile)
                    mangas = adapter.list_mangas().keys()
                    json.dump(mangas, file(cachefile, "w"))
            else:
                mangas = adapter.list_mangas().keys()
                json.dump(mangas, file(cachefile, "w"))

            for manga in mangas:
                print manga

    elif args["manga"] is not None:
        if args["episode"] is not None:
            conf.update({"download_dir": args["download_path"]})
            download_episode(args["manga"], *args["episode"])
        else:
            cachefile = os.path.join(cachedir, u"{s}_{m}_info.json".format(
                s=adapter.slugify(args["site"]),
                m=adapter.slugify(args["manga"])))
            if os.path.exists(cachefile) and args["force"] is False:
                try:
                    info = json.load(file(cachefile))
                except ValueError:
                    os.remove(cachefile)
                    info = adapter.manga_info(name=args["manga"])
                    json.dump(info, file(cachefile, "w"))
            else:
                info = adapter.manga_info(name=args["manga"])
                json.dump(info, file(cachefile, "w"))
            print info
    elif args["episode"] is not None:
        parser.error("--episode requires --manga")
    elif args["download_path"] != conf["download_dir"]:
        parser.error("----download-path requires --episode")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()