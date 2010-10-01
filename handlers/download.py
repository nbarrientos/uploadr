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
from status import FILE_STATUS as fs
import tools

class RequestHandler(BaseHandler):

    def get(self, reference):
        logging.debug("Requesting file %s" % reference)
        if not tools.validate_reference(reference):
            raise tornado.web.HTTPError(404)

        filename, filesize, description, db_uploadid = \
            self._locate_upload(reference)

        if filename is None or filesize is None or description is None:
            raise tornado.web.HTTPError(404)

        filesize, units = tools.format_filesize(filesize)

        reference = tornado.escape.xhtml_escape(reference)
        self.render("fileinfo.html", filename=filename, 
                    filesize=filesize, units=units, 
                    reference=reference, description=description)

    def post(self):
        raise tornado.web.HTTPError(403)

    def _locate_upload(self, reference):
        row = self.db.get("SELECT uploads.name_from_user as n_f_u, \
                    uploads.ext_from_user as e_f_u, files.filesize as fs, \
                    uploads.description as d, uploads.id as i \
                    FROM uploads INNER JOIN files \
                    ON uploads.file_id = files.id \
                    WHERE uploads.reference = '%s' and uploads.status = %u" % 
                    (reference, us['ONLINE']))

        filename = filesize = description = db_uploadid = None
        if row is not None:
            filename = "".join([row['n_f_u'], row['e_f_u']])
            filesize = row['fs']
            description = row['d']
            db_uploadid = row['i']
            
        return (filename, filesize, description, db_uploadid)


class DownloadHandler(BaseHandler):
    
    def get(self, reference, filename):
        # Todo: Validate self.get_argument("token")

        logging.debug("Downloading file %s as %s" % (reference, filename))
        if not tools.validate_reference(reference):
            raise tornado.web.HTTPError(404)
        
        filesize, local_fileid, content_type = self._lookup_upload(reference)

        if filesize is None or local_fileid is None or content_type is None:
            raise tornado.web.HTTPError(404)

        path = "/".join([options.storage, local_fileid])
        logging.debug("About to deliver : %s, Size: %s C-T: %s" % 
                (path, filesize, content_type))

        self.set_header("Content-Length", filesize)
        self.set_header("Content-Type", content_type)

        in_file = open(path, "r")
        buf = in_file.read(100)
        # Todo: EOF flag in in_file?
        while buf != "":
            self.write(buf)
            buf = in_file.read(100)
        in_file.close()

    def post(self):
        raise tornado.web.HTTPError(403)

    def _lookup_upload(self, reference):
        row = self.db.get("SELECT files.local_fileid as l_f, \
                files.content_type as c_t, files.filesize as fs \
                FROM uploads INNER JOIN files \
                ON uploads.file_id = files.id \
                WHERE uploads.reference = '%s' \
                AND uploads.status = %u AND files.status = %u" % 
                (reference, us['ONLINE'], fs['INFS']))

        filesize = local_fileid = content_type = None
        if row is not None:
            filesize = row['fs']
            local_fileid = row['l_f']
            content_type = row['c_t']
        
        return (filesize, local_fileid, content_type)
