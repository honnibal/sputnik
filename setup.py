import os

from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "sputnik", "__about__.py")) as f:
    exec(f.read(), about)


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sputnik = sputnik.__main__:main'
        ]
    },
    install_requires=['semver'],
)
