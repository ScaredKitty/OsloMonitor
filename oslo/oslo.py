from .web import WebUI
from .log import setup_logging

HOST = "localhost"
PORT = 8080


def main():
    setup_logging("INFO")

    web_ui = WebUI(HOST, PORT)
    main_greenlet = web_ui.greenlet
    main_greenlet.join()
