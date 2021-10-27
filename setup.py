# coding: utf-8
import os, re
from setuptools import setup, find_packages, find_namespace_packages

with open(os.path.join("jsparser", "__init__.py"), encoding="utf8") as f:
  version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
  name='jsparser',
  version=version,
  python_requires='>=3.6',
  description='Javascript Parser',
  url='https://github.com/sandin/JSParser',
  author='lds2012',
  author_email='lds2012@gmail.com',
  license='Apache License v2.0',
  include_package_data=True,
  packages=find_namespace_packages(include=['jsparser.*', "jsparser"]),
  entry_points = {
    'console_scripts': [
      'jsparser = jsparser.cli:main'
    ]
  },
  install_requires='''
'''.split('\n'),
  zip_safe=False)
