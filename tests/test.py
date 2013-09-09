import json
from unittest import TestCase

import jwt
import mock

from nose.tools import eq_, ok_
from receipts.receipts import Receipt, Install, VerificationError


class FakeResponse():

    def __init__(self, text):
        self.text = text


class TestReceipt(TestCase):
    cert = jwt.encode({'cert': 'key'}, 'key')
    receipt = jwt.encode({'verify': 'y', 'iat': 1, 'exp': 2}, 'key')

    def test_receipt(self):
        r = Receipt(self.receipt)
        eq_(r.verifier, 'y')
        eq_(r.issue, 1)
        eq_(r.expiry, 2)

    def test_cert(self):
        r = Receipt('{0}~{1}'.format(self.cert, self.receipt))
        eq_(r.cert_decoded()['cert'], 'key')

    @mock.patch('requests.post')
    def test_verify(self, post):
        post.return_value = FakeResponse(json.dumps({'status': 'ok'}))
        r = Receipt(self.receipt)
        eq_(r.verify_server()['status'], 'ok')

    @mock.patch('requests.post')
    def test_verify_fails(self, post):
        post.side_effect = VerificationError
        r = Receipt(self.receipt)
        with self.assertRaises(VerificationError):
            r.verify_server()

    @mock.patch('receipts.certs.ReceiptVerifier')
    def test_crypto(self, rv):
        r = Receipt('{0}~{1}'.format(self.cert, self.receipt))
        ok_(r.verify_crypto())

    def test_crypto_fails(self):
        r = Receipt('{0}~{1}'.format(self.cert, self.receipt))
        with self.assertRaises(VerificationError):
            r.verify_crypto()


class TestInstall(TestCase):
    one = jwt.encode({}, 'key'),
    two = jwt.encode({}, 'key')

    def test_some(self):
        install = Install({'receipts': [self.one, self.two]})
        eq_(len(install.receipts), 2)

    def test_origin(self):
        install = Install({'receipts': [self.one], 'origin': 'http://f.c'})
        eq_(install.origin, 'f.c')
