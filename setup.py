#!/usr/bin/env python

import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='paramobject',
    version_config=True,
    license='Apache-2.0',
    author='Vianney Rousset',
    author_email='vianney@rousset.com',
    description='An easy way to create parametrized object in Python.'
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='github.com/VianneyRousset/paramobject',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Other/Proprietary License'
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7, <3.10',
    install_requires=[],
    setup_requires=['setuptools-git-versioning'],
)

