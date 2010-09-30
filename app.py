import os

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import logging
import uuid

from tornado.options import define, options

from handlers import MainHandler, UploadHandler

define("port", default=8888, help="run on the given port", type=int)
define("storage", default="/tmp/storage", help="FIXME", type=str)
define("desc_min_len", default=15, help="FIXME", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/upload", UploadHandler),
        ]
        settings = dict(
#            cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
#            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
#            xsrf_cookies=True,
#            ui_modules= {"Post": PostModule},
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    logging.getLogger().setLevel(logging.DEBUG)
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
