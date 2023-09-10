#!/usr/bin/python3

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os.path
import urllib.request

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
    #tgbot.send_message(chat_id, "klingeling")
    # XXX: exceptons are not logged right now
    f = urllib.request.urlopen(cfg["intercom-img-url"])
    tgbot.send_photo(chat_id, f, caption=caption)
    
    
class TgDoorBridge(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.server.trigger_path != "" and self.server.trigger_path != self.path:
            logging.debug(f"not a intercom-trigger-path: f{self.path}")
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        tg_send_photo()
        

def main():
    cfg = load_config()
    #logging.basicConfig(level=logging.DEBUG)

    srv = HTTPServer((cfg["hostname"], cfg["port"]), TgDoorBridge)
    srv.trigger_path = cfg.get("intercom-trigger-path", "")
    print("tg door bridge http://%s:%s" % (cfg["hostname"], cfg["port"]))

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

    srv.server_close()



if __name__ == "__main__":
    main()
