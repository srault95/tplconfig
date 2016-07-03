# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from tplconfig.version import version_str

setup(
    name='tplconfig',
    version=version_str(),
    description='Configuration with jinja templates',
    author='Stéphane RAULT',
    author_email='stephane.rault@radicalspam.org',
    url='https://github.com/srault95/tplconfig', 
    license='BSD',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'six',
        'jinja2',
        'PyYAML',
        'requests',
    ],    
    entry_points={
        'console_scripts': [
            'tplconfig = tplconfig.runner:main',
        ],
    },
    tests_require=[
        'nose>=1.0'
    ],
    test_suite='nose.collector',      
    keywords=['jinja2','template','devops'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators'
    ],          
)
