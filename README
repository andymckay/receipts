Receipts
--------------------------------

Parsing of web app receipts in Python.

Includes a desktop client that will allow to parse my Firefox web apps.

Example Python api::

        >>> from receipts.receipts import Receipt
        >>> receipt = Receipt("eyJh....")
        >>> receipt.verifier
        u'https://receiptcheck-marketplace-dev.allizom.org/verify/369802'
        >>> receipt.verify_server()
        {u'status': u'invalid'}
        >>> receipt.verify_crypto()
        True

For more see our docs on: http://readthedocs.org/docs/receipts/en/latest/
