import json
import os
import sys
import argparse
from gettext import ngettext
import urlparse
import ConfigParser
import jwt
import urllib2
from pprint import pprint


directory = os.path.expanduser('~/Library/Application Support/Firefox')
ini = os.path.join(directory, 'profiles.ini')
filename = 'webapps/webapps.json'
server = 'https://receiptcheck-marketplace-dev.allizom.org/verify/%s'


class Apps(object):
    GREEN = "\033[1m\033[92m"
    RED = '\033[1m\033[91m'
    RESET = "\x1B[m"

    def __init__(self):
        self.data = None
        self.path = None

    def _get_domain(self, url):
        return urlparse.urlparse(url)[1]

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

        self.data = json.loads(open(self.path, 'r').read())

    def list(self, *args):
        for k, v in self.data.items():
            rcs = len(v.get('receipts', []))
            receipt_text = ngettext('1 receipt', '%s receipts' % rcs, rcs)
            print u'%s: %s' % (self._good(self._get_domain(v['origin'])),
                               receipt_text)

    def check(self, domain):
        for k, v in self.data.items():
            this_domain = self._get_domain(v['origin'])
            if not domain or domain == this_domain:
                print ('Checking receipts for domain: %s'
                       % self._good(this_domain))
                for r in v.get('receipts', []):
                    cert, receipt = r.split('~')
                    result = jwt.decode(receipt.encode('ascii'), verify=False)
                    verify = result['verify']
                    print 'Verifying at: %s' % self._get_domain(verify)
                    try:
                        response = urllib2.urlopen(result['verify'], r)
                    except urllib2.URLError, error:
                        print 'Server returned: %s' % self._bad(error.code)
                        continue
                    res = json.loads(response.read())['status']
                    print 'Server returned: %s' % self._good(res)
                print

    def expand(self, domain):
        for k, v in self.data.items():
            this_domain = self._get_domain(v['origin'])
            if not domain or domain == this_domain:
                print ('Expanding receipt for domain: %s'
                       % self._good(this_domain))
                receipts = v.pop('receipts')
                pprint(v)
                for r in receipts:
                    cert, receipt = r.split('~')
                    pprint(jwt.decode(cert.encode('ascii'), verify=False))
                    pprint(jwt.decode(receipt.encode('ascii'), verify=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', nargs='?', default='default')
    parser.add_argument('-l', '--list', nargs='?', default=False)
    parser.add_argument('-e', '--expand', nargs='?', default=False)
    parser.add_argument('-c', '--check', nargs='?', default=False)
    result = parser.parse_args()
    apps = Apps()
    for k in ['profile', 'expand', 'list', 'check']:
        v = result.__dict__[k]
        if v is not False:
            getattr(apps, k)(v)


if __name__=='__main__':
    main()

