"""
Release checklist:

[ ] update version
[ ] upload to PyPI
"""

from distutils.core import setup

def get_version(relpath):
    """read version info from file without importing it"""
    from os.path import dirname, join
    for line in open(join(dirname(__file__), relpath)):
        if '__version__' in line:
            if '"' in line:
                # __version__ = "0.9"
                return line.split('"')[1]
            elif "'" in line:
                return line.split("'")[1]

setup(
    name='pager',
    version=get_version('pager.py'),
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
