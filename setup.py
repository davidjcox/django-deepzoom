'''django-deepzoom setup'''
import os
from setuptools import setup, find_packages
import deepzoom as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-deepzoom',
    version=app.__version__,
    packages=['deepzoom'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to create deep zoom tiled images.',
    long_description=open('README.rst').read(),
    url='http://www.invocatum.com/',
    author='David J Cox',
    author_email='davidjcox.at@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

#EOF django-deepzoom setup