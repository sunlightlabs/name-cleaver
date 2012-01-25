import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README'))
readme = f.read()
f.close()

setup(
    name='name-cleaver',
    version='0.2.6',
    description='Name parser and formatter (for politicians, individuals, and organizations)',
    long_description=readme,
    author='Alison Rowland',
    author_email='arowland@sunlightfoundation.com',
    url='http://github.com/sunlightlabs/name-cleaver/',
    package_dir={'': 'name_cleaver'},
    py_modules=['name_cleaver'],
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
        'Topic :: Text Processing :: Linguistic',
    ],
)
