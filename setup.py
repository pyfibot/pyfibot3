#!/usr/bin/env python
from setuptools import setup, find_packages


with open('requirements.txt', 'r') as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(
    name='pyfibot3',
    version='0.01',
    description='',
    author='Pyfibot contributors',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/pyfibot/pyfibot3',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyfibot = pyfibot.core:main',
        ],
    },
    install_requires=requirements,
)
