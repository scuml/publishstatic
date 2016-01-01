#!/usr/bin/env python
import sys
import os
from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = """publishstatic is a django management command that helps automate uploading static files to a server.  Used in conjunction with the ManifestStaticFilesStorage engine, it uploads only changed files to Amazon's S3 and Cloudfront servers.

After collecting static, run ./manange.py publishstatic.  Any changed files will be uploaded to the static file server.
"""

with open('LICENSE') as f:
    license = f.read()

packages = [
    'publishstatic'
]

requires = [
    'boto',
],

setup(
    name='publishstatic',
    version='0.1.0',
    description='Django management command to upload changed static files.',
    long_description=readme,
    author='Stephen Mitchell',
    author_email='stephen@echodot.com',
    url='http://github.com/scuml/publishstatic',
    license=license,
    packages=packages,
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    package_dir={'publishstatic': 'publishstatic'},
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),

)
