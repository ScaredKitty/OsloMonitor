# -*- coding: utf-8 -*-

import logging
import os.path
from datetime import timedelta

import gevent
from flask import Flask, make_response, jsonify, render_template, request
from gevent import pywsgi

from oslo import __version__ as version
from .log import greenlet_exception_logger

logger = logging.getLogger(__name__)
greenlet_exception_handler = greenlet_exception_logger(logger)

DEFAULT_CACHE_TIME = 2.0


class WebUI:
    """
    Set up and run a Flask web app.
    """

    app = None
    greenlet = None
    server = None

    def __init__(self, host, port):
        """
        Create WebUI instance and start running the web server in a separate greenlet.

        :param host: Host/interface that the web server should accept connections to
        :param port: Port that the web server should listen to
        """
        self.host = host
        self.port = port

        # initialize Flask web app.
        app = Flask(__name__)
        self.app = app
        app.debug = True
        app.root_path = os.path.dirname(os.path.abspath(__file__))
        self.app.config["BASIC_AUTH_ENABLED"] = False
        self.app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(seconds=1)
        self.auth = None
        self.greenlet = None

        @app.route('/')
        def index():
            return render_template(
                "index.html",
                # TODO: configurable
                server_name="OSLO DEMO"
            )

        # start the web server
        self.greenlet = gevent.spawn(self.start)
        self.greenlet.link_exception(greenlet_exception_handler)

    def start(self):
        self.__log_config_info()

        self.server = pywsgi.WSGIServer((self.host, self.port), self.app, log=None)
        logger.info("Server start up on " + self.host + ":" + str(self.port))
        self.server.serve_forever()

    def stop(self):
        self.server.stop()

    def __log_config_info(self):
        """
        Print Flask configurations and settings via log in INFO level.
        """
        HEADER = '\n\t[Flask Config]'

        config_dict = self.app.config.copy()

        config_represent_str = ''
        for k in sorted(config_dict):
            v = config_dict[k]
            config_represent_str += ('\n\t' + str(k) + '=' + str(v))

        logger.info(HEADER + config_represent_str)
