# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Garganta',
    version='2',
    packages=['garganta', 'garganta.connectors'],
    install_requires=[
        "beautifulsoup4",
        "awesome-slugify",
        "appdirs",
        "colorama",
        "termcolor",
    ],
    url='www.umutkarci.com',
    license='GPL v2',
    author='cediddi',
    author_email='umutkarci@std.sehir.edu.tr',
    description='A manga download manager.',
    entry_points={
        'console_scripts': [
            'garganta = garganta.main:main'
        ]
    },
)


# sudo python setup.py install
# sudo python setup.py clean -a