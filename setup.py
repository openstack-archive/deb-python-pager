
from distutils.core import setup

setup(
    name='pager',
    version='1.1',
    description='Terminal/console pager module for Python',
    long_description=open('README.rst').read(),
    py_modules=['pager'],
    license='Public Domain',
    author='anatoly techtonik',
    author_email='techtonik@gmail.com',
    url='http://bitbucket.org/techtonik/python-pager',
    classifiers=[
        'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
