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
            self._db_connection = Connection(host="localhost", \
                database="uploadr",\
                user="root")
       
        return self._db_connection

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
            local_fileid = self._get_sha1_sum(f['body'])
            db_fileid, filesize = self._check_file_existance(local_fileid)

            if db_fileid is None:
                filesize = self._save_file_to_disk(f, local_fileid)
                db_fileid = self._save_file_to_db(f, local_fileid, filesize)

            reference = self._save_upload_to_db(db_fileid)

        self.render("uploadsuccess.html", reference=reference, filesize=filesize)

    def _save_file_to_disk(self, f, local_fileid):
        filename = options.storage + "/" + local_fileid
        logging.debug("Writing "+f['filename']+" to "+filename)
        output = open(filename, "w")
        if output is not None:
            output.write(f['body'])
            output.close()
            statinfo = os.stat(filename)
            return statinfo.st_size
        else:
            raise tornado.web.HTTPError(503)

    def _save_file_to_db(self, f, local_fileid, filesize):
        name_from_user, ext_from_user = os.path.splitext(f['filename'])
        content_type = f['content_type']
        db_fileid = self.db.execute("INSERT INTO files (local_fileid, name_from_user, \
                ext_from_user, content_type, filesize) \
                VALUES ('%s','%s','%s', '%s', %u)" % 
                (local_fileid, name_from_user, ext_from_user, content_type,
                filesize))
        #Todo: control execution result
        return db_fileid

    def _save_upload_to_db(self, db_fileid):
        reference = uuid.uuid4()
        client_ip = self.request.remote_ip
        self.db.execute("INSERT INTO uploads \
                (file_id, reference, upload_date, client_ip) \
                VALUES (%u,'%s', NOW(), '%s')" % 
                (db_fileid, reference, client_ip))
        #Todo: control execution result
        return reference

    def _get_sha1_sum(self, filebody):
        generator = hashlib.sha1()
        generator.update(filebody)
        return generator.hexdigest()

    def _check_file_existance(self, filehash):
        row = self.db.get("SELECT id, filesize FROM files \
                    WHERE files.local_fileid='%s'" % filehash)
        if row is not None:
            return (row['id'], row['filesize'])
        return (None, None)
