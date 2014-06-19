import argparse
import ConfigParser
from datetime import date
from gettext import ngettext
import json
from pprint import pprint
import os
import sys
import tempfile
import warnings

from receipts import Install, MissingPyBrowserId, VerificationError


directory = os.path.expanduser('~/Library/Application Support/Firefox')
b2groot = '/data/local/'
ini = os.path.join(directory, 'profiles.ini')


valid_issuers = [
    'marketplace-dev-cdn.allizom.org',
    'marketplace.cdn.mozilla.net',
]


class Firefox(object):
    GREEN = "\033[1m\033[92m"
    RED = '\033[1m\033[91m'
    CYAN = '\033[1m\033[36m'
    RESET = "\x1B[m"
    filename = 'webapps/webapps.json'

    def __init__(self):
        self.data = None
        self.path = None
        self.installs = []

    def _good(self, text):
        return '%s%s%s' % (self.GREEN, text, self.RESET)

    def _bad(self, text):
        return '%s%s%s' % (self.RED, text, self.RESET)

    def profile(self, profile):
        config = ConfigParser.ConfigParser()
        config.readfp(open(ini, 'r'))
        for section in config.sections():
            if (config.has_option(section, 'Name') and
                config.get(section, 'Name') == profile):
                self.path = os.path.join(directory,
                                         config.get(section, 'Path'),
                                         self.filename)
                break

        if not self.path or not os.path.exists(self.path):
            print 'No webapps.json found.'
            sys.exit(1)

        for k, v in json.loads(open(self.path).read()).items():
            self.installs.append(Install(v))

    def list(self, *args):
        for i in self.installs:
            rcs = len(i.receipts)
            receipt_text = ngettext('1 receipt', '%s receipts' % rcs, rcs)
            print u'%s: %s' % (self._good(i.origin), receipt_text)
            for r in i.receipts:
                f = lambda x: date.fromtimestamp(x).strftime('%d %B %y')
                print u'    Issued: %s, expires %s' % (f(r.issue), f(r.expiry))

    def check(self, domain):
        for i in self.installs:
            if not domain or domain == i.origin:
                if i.receipts:
                    print ('%sChecking %s receipt(s) for app:%s %s' %
                           (self.CYAN, len(i.receipts), self.RESET,
                            self._good(i.origin)))
                else:
                    print 'No receipts for app: %s' % self._good(i.origin)
                for r in i.receipts:
                    print 'Verifying at: %s' % r.verifier
                    try:
                        res = r.verify_server()['status']
                    except ValueError, error:
                        print 'Server error: %s' % self._bad(error)
                    except VerificationError, error:
                        print 'Server error: %s' % self._bad(error)
                    else:
                        print 'Server returned: %s' % self._good(res)
                    try:
                        res = r.verify_crypto(valid_issuers=valid_issuers)
                    except VerificationError, error:
                        print 'Validity error: %s' % self._bad(error)
                    except MissingPyBrowserId, error:
                        continue
                    else:
                        states = {True: self._good('good'),
                                  False: self._bad('bad')}
                        print 'Validity check: %s' % states[res]
                    print

    def expand(self, domain):
        for i in self.installs:
            if not domain or domain == i.origin:
                print 'Expanding receipt for domain: %s' % self._good(i.origin)
                print self._good('Install data')
                pprint(i.data)
                for r in i.receipts:
                    if r.cert:
                        print self._good('Certificate data')
                        pprint(r.cert_decoded())
                    print self._good('Receipt data')
                    pprint(r.receipt_decoded())
                print

    def dump(self, domain):
        for i in self.installs:
            if not domain or domain == i.origin:
                print 'Dumping receipt for domain: %s' % self._good(i.origin)
                for r in i.receipts:
                    print r.full


class B2G(Firefox):
    filename = 'webapps/webapps.json'

    def _copy(self, name, dest):
        print 'Copying file from device:', name
        src = '/'.join([b2groot, name])
        dest = os.path.join(dest, name)
        os.system('adb pull %s %s' % (src, dest))
        return dest

    def profile(self, profile):
        dest = tempfile.mkdtemp()
        self.path = self._copy(self.filename, dest)
        if not self.path or not os.path.exists(self.path):
            print 'No webapps.json found.'
            sys.exit(1)

        for k, v in json.loads(open(self.path).read()).items():
            if 'receipts' in v:
                self.installs.append(Install(v))


class Simulator(Firefox):
    filename = 'extensions/r2d2b2g@mozilla.org/profile/webapps/webapps.json'


class File(Firefox):

    def profile(self, profile):
        self.installs.append(Install({
                'receipts': [open(self.filename, 'r').read()],
                'origin': 'file://{0}'.format(self.filename)
            }))


def main():
    warnings.filterwarnings("ignore", category=FutureWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', default='default')
    parser.add_argument('-l', '--list', default=False, action='store_true')
    parser.add_argument('-e', '--expand', default=False, action='store_true')
    parser.add_argument('-c', '--check', default=False, action='store_true')
    parser.add_argument('-a', '--adb', default=False, action='store_true')
    parser.add_argument('-f', '--file', default=False)
    parser.add_argument('-D', '--dump', default=False, action='store_true')
    parser.add_argument('-s', '--simulator', default=False,
        action='store_true')
    parser.add_argument('-d', '--domains', nargs='?', default=False)
    result = parser.parse_args()

    if all([result.simulator, result.adb]):
        print 'Cannot specify both simulator and adb.'
        sys.exit(1)

    if result.simulator:
        print 'Checking Firefox OS simulator.'
        apps = Simulator()
    elif result.adb:
        print 'Checking device via adb.'
        apps = B2G()
    elif result.file:
        print 'Checking file: {0}'.format(result.file)
        apps = File()
        apps.filename = result.file
    else:
        print 'Checking Firefox.'
        apps = Firefox()

    if set([result.list, result.expand, result.check]) == set([False]):
        result.list = True

    apps.profile(result.profile)
    for k in ['expand', 'list', 'check', 'dump']:
        v = result.__dict__[k]
        if v:
            getattr(apps, k)(result.domains)


if __name__=='__main__':
    main()
