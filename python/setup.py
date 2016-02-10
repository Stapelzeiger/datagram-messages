#!/usr/bin/env python

from setuptools import setup

args = dict(
    name='datagrammessages',
    version='0.2',
    description='Send messages and make service calls over a datagram layer',
    packages=['datagrammessages'],
    install_requires=['serial_datagram'],
    author='Patrick Spieler',
    author_email='stapelzeiger@gmail.com',
    url='https://github.com/stapelzeiger/datagram-messages',
    license='BSD'
)

setup(**args)
