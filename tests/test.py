import json
from time import time
from unittest import TestCase

import jwt
import mock

from browserid.errors import ExpiredSignatureError
from nose.tools import eq_, ok_
from receipts import certs
from receipts.receipts import Install, Receipt, VerificationError


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
        self.failUnlessRaises(VerificationError, r.verify_server)

    @mock.patch('receipts.certs.ReceiptVerifier')
    def test_crypto(self, rv):
        r = Receipt('{0}~{1}'.format(self.cert, self.receipt))
        ok_(r.verify_crypto())

    def test_crypto_fails(self):
        r = Receipt('{0}~{1}'.format(self.cert, self.receipt))
        self.failUnlessRaises(VerificationError, r.verify_crypto)



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
        self.failUnlessRaises(certs.InvalidIssuerError,
                certs.fetch_public_key,
                'http://f.c'
            )

    def test_parse(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        ok_(isinstance(res, certs.ReceiptJWT))

    def test_not_sig(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        ok_(not res.check_signature(self.jwk['jwk'][0]))

    def test_sig(self):
        res = certs.parse_jwt(jwt.encode(self.jwk, 'key'))
        self.failUnlessRaises(ValueError, res.check_signature,
            {'alg': 'HS256', 'exp': 'AQAB', 'mod': 'AQAB'})


class TestVerified(TestCase):

    def get_receipt(self, **kw):
        data = {'verify': 'y', 'iat': 1, 'exp': time() + 100}
        data.update(**kw)
        print data
        return jwt.encode(data, 'key')

    def get_cert(self, **kw):
        data = {'cert': 'key', 'iss': 'http://f.c', 'exp': 'AQAB'}
        data.update(**kw)
        return jwt.encode(data, 'key')

    def combine(self, cert, receipt):
        return '%s~%s' % (cert, receipt)

    def test_expired(self):
        self.verifier = certs.ReceiptVerifier()
        self.failUnlessRaises(certs.ExpiredSignatureError,
                self.verifier.verify,
                self.combine(self.get_cert(), self.get_receipt(exp=1))
            )

    def test_certificate_issuer(self):
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        ok_(self.verifier.check_certificate_issuer, 'http://f.c')

    def test_not_certificate_issuer(self):
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        ok_(self.verifier.check_certificate_issuer, 'http://f.b')

    def test_chain_empty(self):
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        self.failUnlessRaises(ValueError,
                self.verifier.verify_certificate_chain,
                None
            )

    def test_chain(self):
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        self.verifier.certs = {'http://f.c': {
            'jwk': [{'alg': 'RSA', 'exp':'AQAB', 'mod': 'AQAB'}]
        }}
        cert = mock.Mock()
        cert.payload = {'iss': 'http://f.c', 'exp': time() + 100,
                        'jwk': [cert]}
        ok_(self.verifier.verify_certificate_chain([cert]))

    def test_chain_expired(self):
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        self.verifier.certs = {'http://f.c': {
            'jwk': [{'alg': 'RSA', 'exp':'AQAB', 'mod': 'AQAB'}]
        }}
        cert = mock.Mock()
        cert.payload = {'iss': 'http://f.c', 'exp': time() - 100,
                        'jwk': [cert]}
        self.failUnlessRaises(ExpiredSignatureError,
                              self.verifier.verify_certificate_chain,
                              [cert])

    @mock.patch('receipts.certs.ReceiptJWT.check_signature')
    @mock.patch('receipts.certs.ReceiptVerifier.verify_certificate_chain')
    def test_pass(self, verify_certificate_chain, check_signature):
        check_signature.return_value = True
        self.verifier = certs.ReceiptVerifier(valid_issuers='f.c')
        self.verifier.certs = {'http://f.c': {
            'jwk': [{'alg': 'RSA', 'exp':'AQAB', 'mod': 'AQAB'}]
            }
        }
        self.verifier.verify(self.combine(self.get_cert(),
                             self.get_receipt()))
