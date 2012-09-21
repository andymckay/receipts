from setuptools import setup, find_packages

setup(
    name='receipts',
    version='0.2.4',
    description='Verify web app receipts',
    long_description=open('readme.rst').read(),
    author='Andy McKay',
    author_email='andym@mozilla.com',
    license='BSD',
    install_requires=['pyjwt', 'requests', 'argparse'],
    py_modules=['receipts'],
    entry_points={
        'console_scripts': [
            'receipts = receipts.fx:main'
        ]
    },
    url='https://github.com/andymckay/receipts',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        ],
    )
