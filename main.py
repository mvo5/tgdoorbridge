#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os.path
import urllib.request
import time

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
    #tgbot.send_message(chat_id, "klingeling")
    f = urllib.request.urlopen(cfg["intercom-img-url"])
    msg=tgbot.send_photo(chat_id, f, caption="klingening")
    # to do: move to thread 
    tg_delete_photo(tgbot, chat_id, msg_id=msg.message_id)


def tg_delete_photo(tgbot, chat_id, msg_id):
    time.sleep(3.600) # 1 hour
    tgbot.delete_message(chat_id,msg_id)

    
    
class TgDoorBridge(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        tg_send_photo()
        

def main():
    cfg = load_config()

    srv = HTTPServer((cfg["hostname"], cfg["port"]), TgDoorBridge)
    print("tg door bridge http://%s:%s" % (cfg["hostname"], cfg["port"]))

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

    srv.server_close()



if __name__ == "__main__":
    main()
