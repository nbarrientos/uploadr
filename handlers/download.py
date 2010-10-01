import os

import tornado.options
import tornado.web

import logging
import uuid
import hashlib
import random

from tornado.options import options

from handlers.base import BaseHandler
from status import UPLOAD_STATUS as us

class RequestHandler(BaseHandler):
    _ERRORS = { 'EDESCTOOSHORT' : "Description is too small (min: %s).",
                'EDESCTOOLONG' : "Description is too long (max: %s)"}

    def get(self, reference):
        logging.debug("Requesting file %s" % reference)
        try:
            uuid.UUID(reference)
        except ValueError:
            raise tornado.web.HTTPError(404)

        filename, filesize = self._request_file(reference)
        logging.debug("Name: %s, Size: %s" % (filename, filesize))

        if filename is None and filesize is None:
            raise tornado.web.HTTPError(404)

        reference = tornado.escape.xhtml_escape(reference)
        self.render("fileinfo.html", filename=filename, 
                    filesize=filesize, reference=reference)

    def post(self):
        raise tornado.web.HTTPError(403)

    def _request_file(self, reference):
        row = self.db.get("SELECT uploads.name_from_user as n_f_u, \
                    uploads.ext_from_user as e_f_u, files.filesize as fs \
                    FROM uploads INNER JOIN files \
                    ON uploads.file_id = files.id \
                    WHERE uploads.reference = '%s' and status = %u" % 
                    (reference, us['ONLINE']))

        filename = filesize = None
        if row is not None:
            filename = "".join([row['n_f_u'], row['e_f_u']])
            filesize = row['fs']
            
        return (filename, filesize)

