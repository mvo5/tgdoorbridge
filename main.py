#!/usr/bin/python3

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os.path
import urllib.request
import time
import threading

import telegram.bot


def load_config():
    with open(os.path.join(os.getenv("SNAP_DARA", "."), "config.json")) as fp:
        cfg = json.load(fp)
    # XXX. validate
    return cfg


def tg_send_photo():
    cfg = load_config()
    tgbot = telegram.bot.Bot(cfg["telegram-bot-token"])
    chat_id = cfg["telegram-chat-id"]
    caption = cfg.get("intercom-img-caption", "ring, ring")
    # XXX: exceptons are not logged right now
    f = urllib.request.urlopen(cfg["intercom-img-url"])
    msg = tgbot.send_photo(chat_id, f, caption=caption)
    t = threading.Thread(target=tg_delete_photo, args=(tgbot, chat_id, msg.message_id))
    t.start()


def tg_delete_photo(tgbot, chat_id, msg_id):
    cfg = load_config()
    delete_delay = cfg.get("intercom-img-delete-delay", 60 * 60 * 60)
    if delete_delay <= 0:
        return
    time.sleep(delete_delay)
    tgbot.delete_message(chat_id, msg_id)


class TgDoorBridge(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        tg_send_photo()


def main():
    cfg = load_config()
    logging.basicConfig(level=logging.INFO)

    srv = HTTPServer((cfg["hostname"], cfg["port"]), TgDoorBridge)
    print("tg door bridge http://%s:%s" % (cfg["hostname"], cfg["port"]))

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

    srv.server_close()


if __name__ == "__main__":
    main()
