# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Garganta',
    version='1',
    packages=['garganta', 'garganta.sites'],
    install_requires=[
        "Mechanize",
        "beautifulsoup4",
        "awesome-slugify",
        "appdirs",
        "wget",
    ],
    url='www.umutkarci.com',
    license='GPL v2',
    author='cediddi',
    author_email='umutkarci@std.sehir.edu.tr',
    description='A manga download manager.',
    entry_points={
        'console_scripts': [
            'garganta = garganta.__main__:main'
        ]
    },
)


# sudo python setup.py install
# sudo python setup.py clean -a