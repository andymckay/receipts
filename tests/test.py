import json
from unittest import TestCase

import jwt
import mock

from nose.tools import eq_, ok_
from receipts import certs
from receipts.receipts import Receipt, Install, VerificationError


class FakeResponse():

    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


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
    receipt = jwt.encode({}, 'key')

    def test_some(self):
        install = Install({'receipts': [self.receipt, self.receipt]})
        eq_(len(install.receipts), 2)

    def test_origin(self):
        install = Install({'receipts': [self.receipt], 'origin': 'http://f.c'})
        eq_(install.origin, 'f.c')


class TestUtils(TestCase):
    jwk = {'jwk': [{'alg': 'RSA'}]}

    @mock.patch('receipts.certs._get')
    def test_fetch(self, _get):
        _get.return_value = FakeResponse(json.dumps(self.jwk))
        ok_(certs.fetch_public_key('http://f.c'))

    @mock.patch('receipts.certs._get')
    def test_error(self, _get):
        _get.return_value = FakeResponse('')
        with self.assertRaises(certs.InvalidIssuerError):
            ok_(certs.fetch_public_key('http://f.c'))

    def test_parse(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        ok_(isinstance(res, certs.ReceiptJWT))

    def test_not_sig(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        ok_(not res.check_signature(self.jwk['jwk'][0]))

    def test_sig(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        with self.assertRaises(ValueError):
            # Not sure why, but HS256 is not valid.
            ok_(not res.check_signature({'alg': 'HS256', 'exp': 'AQAB',
                                         'mod': 'AQAB'}))


class TestVerified(TestCase):

