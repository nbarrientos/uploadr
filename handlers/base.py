import tornado.options
import tornado.web

from tornado.options import options
from tornado.database import Connection

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        # Todo: Get from config
        if not hasattr(self, "_db"):
            self._db_connection = Connection(host="localhost", \
                database="uploadr",\
                user="root")
       
        return self._db_connection
