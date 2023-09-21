#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='animethemes-batch-encoder',
    version='2.1',
    author='AnimeThemes',
    author_email='admin@animethemes.moe',
    url='https://github.com/AnimeThemes/animethemes-batch-encoder',
    description='Generate/Execute FFmpeg commands for files in acting directory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'appdirs',
        'inquirer'
    ],
)
