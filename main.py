import curses
import time
import pathlib, hypixel_api
from application import *


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()

    config_path = pathlib.Path('~/.config/hypixel_api').expanduser()

    apikey = None
    while apikey == None:
        if config_path.joinpath('key.txt').exists() or config_path.joinpath('key.gpg').exists():
            apikey = RetrieveKey(stdscr)

        else:
            apikey = StoreApiKey(stdscr)

    hypixel = hypixel_api.SkyblockApi(apikey)
    keyinfo = hypixel.Key()
    if not keyinfo.get('success', False):
        NotifyApiKeyError(stdscr, keyinfo.get('cause', 'API_ERROR!'))

    else:
        StartApiInterface(stdscr, hypixel)

    curses.curs_set(1)


if __name__ == '__main__':
    curses.wrapper(main)
