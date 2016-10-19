# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='nyaa-cli',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1.dev5',

    description='Anime Stream CLI for torrents and online videos',
    long_description='Anime Stream CLI for torrents and online videos',

    # The project's main homepage.
    url='https://github.com/setr/animestreamer-cli',

    # Author details
    author='Neil Okhandiar',
    author_email='nokhand@gmail.com',

    # Choose your license
    license='GPLv3',

    classifiers=[
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: End Users/Desktop',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
        ],
    keywords='webtorrent anime',
    packages=find_packages(),
    install_requires=['beautifulsoup4',
                        'attrs',
                        'click',
                        'cfscrape'],
    entry_points={
        'console_scripts': [
            'nyaa = nyaa.__main__:main',
        ],
    }
)


