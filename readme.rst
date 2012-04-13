Receipts
--------------------------------

Creates a python script called receipts that will find Web App receipts in
your Firefox install and then allows you to check them against the verification
service contained within the receipt.

Tested on OS X, not sure about support for other operating systems yet.

Install
---------------------------------

Requirements: Python 2.7

To install::

  pip install receipts

This will install pyjwt and requirements.

Usage
---------------------------------

To list receipts::

  receipts -l

To check a receipt::

  receipts -c DOMAINNAME

By default receipts will try and find your default Firefox profile. If not it
will use one provided with -p, eg::

  receipts -l -p fx6

License
----------------------------------

MIT
