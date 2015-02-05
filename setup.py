'''django-deepzoom setup'''

import os
from setuptools import setup, find_packages
import deepzoom as app


def file_read(filename):
    try:
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        return ''


README = file_read('README.rst')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-deepzoom',
    version=app.__version__,
    packages=['deepzoom'],
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to create deep zoom tiled images.',
    long_description=file_read('README.rst'),
    url='http://django-deepzoom.invocatum.net/',
    author='David J Cox',
    author_email='davidjcox.at@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    install_requires=[
                      'django>=1.4',
                      'pillow>=1.7.8',
                      'six>=1.9.0',
    ],
    keywords='imaging zoomable images deepzoom openseadragon',
    zip_safe=False,
)

#EOF - django-deepzoom setup