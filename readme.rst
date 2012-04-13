Receipts
--------------------------------

Creates a python script called receipts that will find Web App receipts in
your Firefox install and then allows you to check them against the verification
service contained within the receipt.

Tested on OS X, not sure about support for other operating systems yet.

Install
---------------------------------

Requirements: Python 2.7 and Firefox 14

To install::

  pip install receipts

This will install pyjwt and requirements.

Usage
---------------------------------

To list receipts::

  receipts -l

To check a receipt for a specific domain::

  receipts -c DOMAINNAME

To check all domains::

  receipts -c

To expand a receipt for a specific domain::

  receipts -e DOMAINNAME

To expand all domains::

  receipts -e

By default receipts will try and find your default Firefox profile. If not it
will use one provided with -p, eg::

  receipts -l -p fx6

Screenshots
----------------------------------

http://cl.ly/0S2J1V3f123L1H3C3l1z
http://cl.ly/2y220K1U3G322z26023v

License
----------------------------------

MIT
