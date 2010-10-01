import tornado.options
import tornado.web

from handlers.base import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        hosted_files = self._count_hosted_files()
        self.render("uploadform.html", hosted_files=hosted_files)

    def post(self):
        raise tornado.web.HTTPError(403)

    def _count_hosted_files(self):
        row = self.db.get("SELECT COUNT(*) as c FROM files")
        if row is not None: 
            row = row['c']
        return row
