# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='iomod',
    version='1.1',
    description='read/write text file module',
    author='Takeki Shikano',
    author_email='',
    url=None,
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)

