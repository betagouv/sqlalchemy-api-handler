import io
import pathlib
import os
import re

from setuptools import setup


HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / 'requirements.txt').read_text().splitlines()
TESTS_REQUIRE = (HERE / 'requirements-test.txt').read_text().splitlines()[1:]

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open("{}/__init__.py".format(os.environ.get('MODULE_NAME')), "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read(), re.M).group(1)

setup(name=os.environ.get('PIP_NAME'),
      version=version,
      url='https://github.com/{}'.format(os.environ.get('GITHUB_NAME')),
      project_urls={
        'Code': 'https://github.com/{}'.format(os.environ.get('GITHUB_NAME')),
        'Issue tracker': 'https://github.com/{}/issues'.format(os.environ.get('GITHUB_NAME')),
      },
      license='MPL-2.0',
      author='Erwan Ledoux',
      author_email='lawanledoux@gmail.com',
      maintainer='Ledoux',
      maintainer_email='lawanledoux@gmail.com',
      description='Adds SQLAlchemy support to your Flask application for handle apis.',
      long_description=readme,
      long_description_content_type='text/markdown',
      packages=[
        'sqlalchemy_api_handler',
        'sqlalchemy_api_handler.bases',
        'sqlalchemy_api_handler.mixins',
        'sqlalchemy_api_handler.serialization',
        'sqlalchemy_api_handler.utils'
      ],
      include_package_data=True,
      python_requires=">= 2.7, != 3.0.*, != 3.1.*, != 3.2.*, != 3.3.*",
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
       ],
)
