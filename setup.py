from name_cleaver import __version__
from setuptools import setup, find_packages
import os

f = open(os.path.join(os.path.dirname(__file__), 'README'))
readme = f.read()
f.close()

setup(
    name='name-cleaver',
    version=__version__,
    description='Name parser and formatter (for politicians, individuals, and organizations)',
    long_description=readme,
    author='Alison Rowland',
    author_email='arowland@sunlightfoundation.com',
    url='http://github.com/sunlightlabs/name-cleaver/',
    packages=find_packages(),
    license='BSD License',
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
