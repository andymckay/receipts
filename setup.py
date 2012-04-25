import os
from setuptools import setup


setup(
    name='receipts',
    version='0.1.5',
    description='Verify web app receipts',
    long_description=open('readme.rst').read(),
    author='Andy McKay',
    author_email='andym@mozilla.com',
    license='BSD',
    install_requires=['pyjwt'],
    py_modules=['receipts'],
    entry_points={
        'console_scripts': [
            'receipts = receipts:main'
        ]
    },
    url='https://github.com/andymckay/receipts',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        ],
    )
