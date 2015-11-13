from setuptools import setup, find_packages

setup(
    name='sputnik',
    version='0.1.0',
    description='Sputnik data package manager library',
    url='https://github.com/henningpeters/sputnik',
    author='Henning Peters',
    author_email='hp@spacy.io',
    license='MIT',
    packages=find_packages(),
    install_requires=['semver'],
)
