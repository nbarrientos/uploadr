import tornado.web

import logging

from handlers.base import BaseHandler
from status import UPLOAD_STATUS as us

class DeleteHandler(BaseHandler):

    def get(self, reference):
        raise tornado.web.HTTPError(403)

    def post(self, reference):
        token = self.get_argument("token", default=None)
        if token is None:
            raise tornado.web.HTTPError(400)

        if self._validate_delete_token(token, reference):
            self._delete_reference(reference)
            self.redirect("/") # Fixme?
        else:
            logging.debug("Removal denied for delete token %s" % token)
            raise tornado.web.HTTPError(403)

    def _validate_delete_token(self, token, reference):
        logging.debug("Validating delete token %s for reference %s" % 
                    (token, reference))
        row = self.db.get("SELECT uploads.remove_token FROM uploads \
                WHERE uploads.remove_token = '%s' \
                AND uploads.reference = '%s' \
                AND uploads.status = %u" % 
                (token, reference, us['ONLINE']))

        return row is not None

    def _delete_reference(self, reference):
        logging.debug("Setting DELETED status to upload reference %s" % reference)
        row = self.db.execute("UPDATE uploads SET status=%u \
                WHERE reference = '%s'" %
                (us['DELETED'], reference))

        if row is None:
            raise RuntimeError("Upload removal failed: %s" % reference)
