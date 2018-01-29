# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='iomod',
    version='1.0',
    description='related input/output module.',
    author='shikano takeki',
    author_email='shikano.takeki@nexon.co.jp',
    url=None,
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)

