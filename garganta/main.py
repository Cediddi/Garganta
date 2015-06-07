# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import shutil

import colorama
from termcolor import colored

from garganta.connectors import get_connector
from garganta.settings import settings


def download(*episodes):
    from garganta.downloader import start_download
    from garganta.utils import create_folder

    for episode in episodes:
        connector = episode.manga.connector
        folder = create_folder(episode)
        pages = connector.get_page_list(episode)
        print(colored("{manga} - #{no} {episode}".format(
            manga=episode.manga.name, no=episode.no, episode=episode.name),
            "magenta"))
        for page in pages:
            settings["queue"].append((page, folder))

    start_download()
    print(" " * shutil.get_terminal_size().columns, end="")
    print("\r" * shutil.get_terminal_size().columns, end="")
    print(colored("All downloads done", "green", attrs=["bold"]))


def init_parser():
    arg_parser = ArgumentParser("Garganta")

    arg_parser.add_argument("-c", "--connector",
                            action='store',
                            default=settings["defaultconnector"],
                            choices=["manga-tr", "mangaturk"],
                            help="site you want to use, Default: {}".format(
                                settings["defaultconnector"]))

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

    arg_parser.add_argument("-d", "--downloadpath", action='store',
                            default=settings["downloadpath"],
                            help="Download path you want to use")

    arg_parser.add_argument("-f", "--force", action='store_true',
                            help="Ignores local cache")

    arg_parser.add_argument("-t", "--thread", action='store', type=int,
                            default=3, help="Concurrent download count")

    arg_parser.add_argument("-i", "--invalidate", action='store_true',
                            help="Invalidates local cache, use with caution")

    return vars(arg_parser.parse_args()), arg_parser


def main():
    colorama.init()
    args, parser = init_parser()

    if args["manga"] is not None:
        args["manga"] = " ".join(args["manga"]).lower()
    else:
        args["manga"] = None

    settings.update({
        "downloadpath": args["downloadpath"],
        "poolsize": args["thread"],
        "cachestatus": not args["force"],
    })

    connector = get_connector(args["connector"])

    if connector is None:
        parser.print_help()
        exit()

    if args["invalidate"]:
        temp = (
            colored("Are you really sure to invalidate caches?",
                    "red", attrs=["bold"]),
            colored("(y,N) :", "green")
        )
        response = input(" ".join(temp))
        if response.lower() == "y":
            settings["cacheadapter"].invalidate(connector.get_name())
            print("Connector cache Invalidated")
            quit()
        quit()

    if args["list"] and args["manga"] and args["episode"]:
        header = colored("#{no} {name}:", "cyan")
        row = colored("\t{no}\t{url}", "blue")
        data = []
        manga = connector.manga_from_name(args["manga"])
        for ep_no in args["episode"]:
            episode = connector.episode_from_no(manga, int(ep_no))
            if not episode:
                print(colored("Episode {no} does not exist".format(no=ep_no),
                              "red", attrs=["bold"]))
                continue
            data.append(header.format(no=episode.no, name=episode.name))
            pages = sorted(connector.get_page_list(episode),
                           key=lambda x: x.no)
            [data.append(row.format(no=p.no, url=p.url)) for p in pages]
            data.append("")

        if data:
            print(*data, sep="\n")

    elif args["list"] and args["manga"]:
        row = colored("#{no} {name}", "cyan")
        data = []
        manga = connector.manga_from_name(args["manga"])
        episodes = sorted(connector.get_episode_list(manga),
                          key=lambda x: x.no)
        [data.append(row.format(no=ep.no, name=ep.name)) for ep in episodes]
        print(*data, sep="\n")

    elif args["list"]:
        row = colored("{name}", "green", attrs=["bold"])
        data = []
        mangas = sorted(connector.get_manga_list(), key=lambda x: x.name)
        [data.append(row.format(name=manga.name)) for manga in mangas]
        print(*data, sep="\n")

    elif args["manga"] and args["episode"]:
        """download episode"""
        manga = connector.manga_from_name(args["manga"])
        episodes = []
        for ep_no in args["episode"]:
            episode = connector.episode_from_no(manga, int(ep_no))
            if not episode:
                print(colored("Episode {no} does not exist".format(no=ep_no),
                              "red", attrs=["bold"]))
                continue
            episodes.append(episode)

        download(*episodes)

    elif args["manga"]:
        import textwrap
        import shutil

        header = colored("{name}:", "green", attrs=["bold"])
        row = colored("\t#{no} {name}", "cyan")

        data = []
        manga = connector.manga_from_name(args["manga"])
        data.append(header.format(name=manga.name))
        data.append("")
        info = connector.get_manga_info(manga)
        wrapped_info = textwrap.wrap(info,
                                     width=shutil.get_terminal_size().columns)
        [data.append(colored(l, "yellow")) for l in wrapped_info]
        data.append("")
        episodes = sorted(connector.get_episode_list(manga),
                          key=lambda x: x.no)
        [data.append(row.format(no=ep.no, name=ep.name)) for ep in episodes]
        print(*data, sep="\n")
    else:
        parser.print_help()
