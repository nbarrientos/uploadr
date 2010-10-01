import tornado.web
import tornado.options

import logging
import uuid
import hashlib
import random

from tornado.options import options

from handlers.base import BaseHandler
import tools

class TokenHandler(BaseHandler):

    def get(self):
        token = self._generate_and_save_download_token()
        data = { "s": 0, "t": token }
        if token is None:
            data['r'] = "Too many tokens requested per IP"
            data['s'] = 1
        json = tornado.escape.json_encode(data)
        
        if token is not None:
            logging.debug("Serving token %s to IP address %s" %
                        (token, self.request.remote_ip))

        self.set_header("Content-Type", "application/json")
        self.write(json)

    def post(self):
        raise tornado.web.HTTPError(403)

    def _generate_and_save_download_token(self):
        if not self._more_tokens_allowed():
            return None

        token = tools.generate_download_token()
        while not self._is_download_token_free(token):
            token = tools.generate_download_token()

        client_ip = self.request.remote_ip
        self.db.execute("INSERT INTO tokens \
                (token, ip, expires) \
                VALUES ('%s', '%s', NOW() + INTERVAL 1 HOUR)" %
                (token, client_ip))

        return token

    def _more_tokens_allowed(self):
        row = self.db.get("SELECT COUNT(token) as c FROM tokens \
                WHERE tokens.ip = '%s'" % self.request.remote_ip)
        allowed = True
        if row is not None and row['c'] >= options.max_tokens_per_ip:
            allowed = False
        return allowed

    def _is_download_token_free(self, token):
        row = self.db.get("SELECT tokens.token as t \
                           FROM tokens \
                           WHERE tokens.token = '%s'" % token)
        return row is None
