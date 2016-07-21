#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Packing metadata for setuptools."""


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'hamster-lib',
]

setup(
    name='hamster-gtk',
    version='0.10.0',
    description="A GTK interface to the hamster time tracker.",
    long_description=readme + '\n\n' + history,
    author="Eric Goller",
    author_email='eric.goller@projecthamster.org',
    url='https://github.com/projecthamster/hamster-gtk',
    packages=find_packages(),
    install_requires=requirements,
    license="GPL3",
    zip_safe=False,
    keywords='hamster-gtk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points='''
    [gui_scripts]
    hamster-gtk=hamster_gtk.hamster_gtk:_main
    '''
)
