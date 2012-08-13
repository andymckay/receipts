import argparse
import ConfigParser
from datetime import date
from gettext import ngettext
import json
from pprint import pprint
import os
import sys
import warnings

from receipts import Install, MissingPyBrowserId, VerificationError


directory = os.path.expanduser('~/Library/Application Support/Firefox')
ini = os.path.join(directory, 'profiles.ini')
filename = 'webapps/webapps.json'


class Firefox(object):
    GREEN = "\033[1m\033[92m"
    RED = '\033[1m\033[91m'
    RESET = "\x1B[m"

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
                                         filename)
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
                print 'Checking receipts for domain: %s' % self._good(i.origin)
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
                        res = r.verify_crypto()
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


def main():
    warnings.filterwarnings("ignore", category=FutureWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', nargs='?', default='default')
    parser.add_argument('-l', '--list', nargs='?', default=False)
    parser.add_argument('-e', '--expand', nargs='?', default=False)
    parser.add_argument('-c', '--check', nargs='?', default=False)
    result = parser.parse_args()
    apps = Firefox()
    for k in ['profile', 'expand', 'list', 'check']:
        v = result.__dict__[k]
        if v is not False:
            getattr(apps, k)(v)


if __name__=='__main__':
    main()
