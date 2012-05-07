Receipt Library
===============

Note: this API is just being built and is liable to change.

Receipt object
--------------

Allows you to inspect a receipt. In the following I snipped the receipt string
because it's really long::

        >>> from receipts.receipts import Receipt
        >>> receipt = Receipt("eyJh....")
        >>> receipt.verifier
        u'https://receiptcheck-marketplace-dev.allizom.org/verify/369802'
        >>> receipt.verify_server()
        {u'status': u'invalid'}
        >>> receipt.verify_crypto()
        True

* `verify_server`: will send the receipt to the URL specified in the receipt
  for verification and return its result.

* `verify_crypto`: this requires PyBrowserID to be installed. This is optional
  and is not installed in the setup due to its dependencies. If you don't have
  this installed: `MissingPyBrowserId` is raised.
