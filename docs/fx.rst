Firefox receipt parser
======================

This requires Firefox 14 and Python 2.7 or greater to be installed.

Creates a python script called receipts that will find Web App receipts in
your Firefox install and then allows you to check them against the verification
service contained within the receipt.

Tested on OS X, not sure about support for other operating systems yet.

Usage
~~~~~

To list receipts::

  receipts -l

To check a receipt for a specific domain. This will check the receipt against
the server and check that it is cryptographically correct. These are two
different steps::

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

Example:

.. image:: fx.png
