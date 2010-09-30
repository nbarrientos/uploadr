import os

import tornado.options
import tornado.web

import logging
import uuid
import hashlib

from tornado.options import options
from tornado.database import Connection

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        # Todo: Get from config
        if not hasattr(self, "_db"):
            self._db = Connection(host="localhost", \
                database="uploadr",\
                user="root")
       
        return self._db

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

class UploadHandler(BaseHandler):
    def get(self):
        raise tornado.web.HTTPError(403)

    def post(self):
        for f in self.request.files['payload']:
                local_fileid, filesize = self._save_file_to_disk(f)
                fileid = self._save_file_to_db(f, local_fileid, filesize)

        self.render("uploadsuccess.html", fileid=fileid, filesize=filesize)

    def _save_file_to_disk(self, f):
        # Todo: Check if the file already exists (SHA1), if so, locate 
        # it and simply return it

        # The file does not exist, we must create it now
        local_fileid = str(uuid.uuid4())
        filename = options.storage + "/" + local_fileid
        logging.debug("Writing "+f['filename']+" to "+filename)
        output = open(filename, "w")
        if output is not None:
            output.write(f['body'])
            output.close()
            statinfo = os.stat(filename)
            return (local_fileid, statinfo.st_size)
        else:
            raise tornado.web.HTTPError(503)

    def _save_file_to_db(self, f, local_fileid, filesize):
        name_from_user, ext_from_user = os.path.splitext(f['filename'])
        content_type = f['content_type']
        sha1hash = self._get_sha1_sum(f['body'])
        ret = self.db.execute("INSERT INTO files (local_fileid, name_from_user, \
                ext_from_user, content_type, filesize, sha1) \
                VALUES ('%s','%s','%s', '%s', %u, '%s')" % \
                (local_fileid, name_from_user, ext_from_user, content_type,
                filesize, sha1hash))
        #Todo: control execution result
        return ret

    def _get_sha1_sum(self, filebody):
        generator = hashlib.sha1()
        generator.update(filebody)
        return generator.hexdigest()
