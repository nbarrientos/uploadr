import os

import tornado.options
import tornado.web

import logging
import uuid
import hashlib
import random
import mimetypes

from tornado.options import options

from handlers.base import BaseHandler
import tools

class UploadHandler(BaseHandler):
    _ERRORS = { 'EDESCTOOSHORT' : "Description is too small (min: %s).",
                'EDESCTOOLONG' : "Description is too long (max: %s)"}

    def get(self):
        raise tornado.web.HTTPError(403)

    def post(self):
        desc = tornado.escape.xhtml_escape(self.get_argument("description"))
        reason = None
        # Todo: Refactor, extract method
        if len(desc) < options.desc_min_len:
            reason = self._ERRORS['EDESCTOOSHORT'] % options.desc_min_len
        elif len(desc) > options.desc_max_len:
            reason = self._ERRORS['EDESCTOOLONG'] % options.desc_max_len

        if reason is not None:
            self.render("uploadfailure.html", reason=reason)

        # All right!
        for f in self.request.files['payload']:
            local_fileid = self._get_sha1_sum(f['body'])
            db_fileid, filesize = self._check_file_existence(local_fileid)

            if db_fileid is None:
                filesize = self._save_file_to_disk(f, local_fileid)
                db_fileid = self._save_file_to_db(f, local_fileid, filesize)

            reference, remove_token = self._save_upload_to_db(f, db_fileid, desc)

        filesize, units = tools.format_filesize(filesize)

        logging.debug("New reference created: %s" % reference)

        self.render("uploadsuccess.html",
            reference=reference, filesize=filesize, 
            units=units, remove_token=remove_token)

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
        filename = tornado.escape.xhtml_escape(f['filename'])
        content_type = mimetypes.guess_type(filename)[0]
        if content_type is None:
            content_type = "application/octet-stream"
        db_fileid = self.db.execute("INSERT INTO files (local_fileid, \
                content_type, filesize) \
                VALUES ('%s', '%s', %u)" % 
                (local_fileid, content_type, filesize))
        #Todo: control execution result
        return db_fileid

    def _save_upload_to_db(self, f, db_fileid, description):
        reference = uuid.uuid4().hex
        client_ip = self.request.remote_ip
        remove_token = tools.generate_remove_token()
        filename = tornado.escape.xhtml_escape(f['filename'])
        name_from_user, ext_from_user = os.path.splitext(filename)
        self.db.execute("INSERT INTO uploads \
                (file_id, reference, upload_date, client_ip, \
                remove_token, description, name_from_user, ext_from_user) \
                VALUES (%u,'%s', NOW(), '%s', '%s', '%s', '%s', '%s')" % 
                (db_fileid, reference, client_ip, remove_token, 
                description, name_from_user, ext_from_user))
        #Todo: control execution result
        return (reference, remove_token)

    def _get_sha1_sum(self, filebody):
        generator = hashlib.sha1()
        generator.update(filebody)
        return generator.hexdigest()

    def _check_file_existence(self, filehash):
        row = self.db.get("SELECT id, filesize FROM files \
                    WHERE files.local_fileid='%s'" % filehash)
        if row is not None:
            return (row['id'], row['filesize'])
        return (None, None)
