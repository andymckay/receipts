Receipt documentation
====================================

Contents:

.. toctree::
   :maxdepth: 2

   fx.rst
   lib.rst

Install
-------

Requires Python 2.7 and pip::

        pip install receipts

Dependencies that will be installed:

* requests
* pyjwt

Optional dependency:

* PyBrowserID

This is required for the crypto verficition check of the receipt. The
verification server will do this for you, but you can optionally do it
yourself. To install this::

    pip install PyBrowserID

Changes:

* 0.2.2

  Make PyBrowserID and hence M2Crypto optional. Add in issue and expiry dates
  into the list command nicely formatted.

License
----------------------------------

MIT

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

