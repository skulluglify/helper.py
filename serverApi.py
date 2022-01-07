import os, json, re#, sys
from urllib import parse
from types import NoneType
from typing import Any, Callable, Union
from flask import Flask, request, jsonify#, render_template
from flask.logging import default_handler
from logging import INFO, FileHandler#, getLogger
from logging.config import dictConfig
# from werkzeug.wrappers import response

from tools import parseIntAuto

def parse_params_auto(params: str):

    if type(params) is str:

        if not params.startswith("?"):

            params = "?" + params;
        
        d: dict = dict(parse.parse_qsl(parse.urlsplit(params).query))

        if not len(d.items()):

            return params.__getitem__(slice(1,len(params)))

        return d

    return None

pwd: str = os.path.dirname(os.path.abspath(__file__))
cwd: str = os.getcwd()

f: type = Union[dict, list, NoneType]

dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(levelname)s]: %(message)s" # %(module)s
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "wsgi"
        ]
    }
})

# @app.route("/hello/", methods=["GET", "POST"])
# def welcome():
#     return jsonify({
#         "message": "say hello!"
#     })

default_header_keys: list = ["User-Agent", "Accept", "Postman-Token", "Host", "Accept-Encoding", "Connection", "Content-Length", "Content-Type"]
default_header_keys: list = [*map(lambda x: x.lower(), default_header_keys)]

def parse_url_auto(o: Any):

    if (type(o) is dict):

        x: list = o.items()

        if not len(x):

            return None

        for (k, v) in x:

            o.__setitem__(parseIntAuto(k), parse_url_auto(v))

        return o
    
    if (type(o) is list):

        x: list = [*enumerate(o)]

        if not len(x):

            return None

        for (k, v) in x:

            o.__setitem__(k, parse_url_auto(v))

        return o

    if (type(o) is str):

        if "=" in (o):

            return parse_url_auto(dict(parse.parse_qsl(o)))

        d: f = None

        try:

            d = json.loads(o.replace("\'", "\""))

        except json.decoder.JSONDecodeError as e:

            return str
        
        finally:

            return parse_url_auto(d)

    if (type(o) is int):

        return o

    if (type(o) is bool):

        return o

    if (type(o) is NoneType):

        return o
    
    return None

class ServerApi:

    def __init__(self, *args, **kwargs):

        self.name = "__MAIN__" ## bypass

        self.__dict__.update(kwargs)

        self.app = Flask(self.name)

        self.app.config.update({
            "ENV": "development"
        })

        self.app.before_first_request(self.before_first_request)

    def before_first_request(self):

        log_level = INFO

        self.app.logger.removeHandler(default_handler)

        # log = getLogger("werkzeug")
        # log.propagate = False
        # log.disabled = True
    
        for handler in self.app.logger.handlers:
        #    self.app.logger.removeHandler(handler)
            print(handler)
    
        logdir = os.path.join(cwd, "logs")

        if not os.path.exists(logdir):

            os.mkdir(logdir)
        
        log_file = os.path.join(logdir, "app.log")
        
        handler = FileHandler(log_file)
        handler.setLevel(log_level)

        self.app.logger.addHandler(handler)
    
        self.app.logger.setLevel(log_level)

    def run(self, **kwargs):

        config: dict = {

            "threaded": True, 
            "port": "5000", 
            "debug": False
        
        }

        config.update(kwargs)

        self.app.run(**config)

    def routeJSON(self, **kwargs):

        def decorator(callback: Callable):

            def wrapper(name):

                data: f = {}

                """
                ?COLLECT ALL DATA MAPS
                """
                data_args: dict = dict([ (k, parse_params_auto(v)) for (k, v) in request.args.to_dict().items() ])
                data_headers: f = parse_url_auto(dict([ (k, v) for (k, v) in request.headers.items(lower = True) if not k in default_header_keys]))
                data_responses: f = None if not request.is_json else request.get_json()

                data = data_responses or data_args or data_headers

                if callable(callable):

                    data = callback(path = name, response = data)

                    if data:

                        return jsonify(data)

                return jsonify({})

            r: Callable = self.app.route("/<string:name>", **kwargs)
            r(wrapper)

        return decorator


if str(__name__).upper() in ("__MAIN__",):

    server = ServerApi(name=__name__)

    @server.routeJSON(methods=["GET", "POST"])
    def wrapper(path, response):

        print(path)
        print(response)

        return response

    server.run()
