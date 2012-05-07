import argparse
import ConfigParser
from gettext import ngettext
import json
import jwt
from pprint import pprint
import os
import sys
import urlparse

import requests
from requests.exceptions import RequestException

try:
    import certs
    CERTS = True
except ImportError:
    CERTS = False


class VerificationError(Exception):
    pass


class MissingPyBrowserId(Exception):
    pass


class Receipt(object):

    def __init__(self, data):
        self.receipt = ''
        self.cert = ''
        self.full = data
        self.decoded = {}
        if '~' in data:
            self.cert, self.receipt = data.split('~')
        else:
            self.receipt = data

    def cert_decoded(self):
        return jwt.decode(self.cert.encode('ascii'), verify=False)

    def receipt_decoded(self):
        if not self.decoded:
            self.decoded = jwt.decode(self.receipt.encode('ascii'),
                                      verify=False)
        return self.decoded

    @property
    def verifier(self):
        return self.receipt_decoded()['verify']

    @property
    def issue(self):
        return self.receipt_decoded()['iat']

    @property
    def expiry(self):
        return self.receipt_decoded()['exp']

    def verify_server(self):
        try:
            response = requests.post(self.verifier, self.full)
        except RequestException, error:
            raise VerificationError(error)
        return json.loads(response.text)

    def verify_crypto(self):
        if not CERTS:
            raise MissingPyBrowserId('Requires optional dependency: '
                                     'pip install PyBrowserID')
        try:
            return certs.ReceiptVerifier().verify(self.full)
        except Exception, error:
            raise VerificationError(error)


class Install(object):

    def __init__(self, data):
        self.data = data
        self.receipts = []
        for r in self.data.get('receipts', []):
            self.receipts.append(Receipt(r))
        del self.data['receipts']

    @property
    def origin(self):
        return urlparse.urlparse(self.data['origin'])[1]
