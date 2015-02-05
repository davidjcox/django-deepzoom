# Django settings for django-deepzoom test project.

import os

from deepzoom.utils import is_django_version_greater_than


DEBUG = True

TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

SECRET_KEY = 'django-deepzoom-test-secret'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': ':memory:', 
    }
}


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))


STATIC_ROOT = os.path.abspath(os.path.join(TEST_ROOT, 'test_static'))

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.abspath(os.path.join(TEST_ROOT, 'test_exec'))

MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.abspath(os.path.join(TEST_ROOT, 'test_static')), 
)

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(TEST_ROOT, '../templates/deepzoom')), 
)

EXTERNAL_APPS = [
    'django.contrib.contenttypes', 
    'django.contrib.messages', 
    'django.contrib.sessions', 
    'django.contrib.sites', 
]

DJANGO_APP_STARTABLE = is_django_version_greater_than(1, 6)

if DJANGO_APP_STARTABLE:
    deepzoom = 'deepzoom.apps.DeepZoomAppConfig'
else:
    deepzoom = 'deepzoom'

INTERNAL_APPS = [
    deepzoom, 
    'deepzoom.test',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

MIDDLEWARE_CLASSES = (
)


#===django-deepzoom settings====================================================


#  This is the directory appended to MEDIA_ROOT for storing uploaded images.
#  If defined, but not physically created, the directory will be created for you.
#  If not defined, the following default directory name will be used:
UPLOADEDIMAGE_ROOT = 'uploaded_images'

#  These are the keyword arguments used to initialize the deep zoom creator:
#  'tile_size', 'tile_overlap', 'tile_format', 'image_quality', 'resize_filter'.
#  They strike a good (maybe best?) balance between image fidelity and file size.
#  If not defined the following default values will be used:
DEEPZOOM_PARAMS = {'tile_size': 256,
                    'tile_overlap': 1,
                    'tile_format': "jpg",
                    'image_quality': 0.85,
                    'resize_filter': "antialias"}

#  This is the directory appended to MEDIA_ROOT for storing generated deep zooms.
#  If defined, but not physically created, the directory will be created for you.
#  If not defined, the following default directory name will be used:
DEEPZOOM_ROOT = 'deepzoom_images'

#  This is the default setting for the `create_deepzoom` attribute in the 
#  `UploadedImage` class that determines whether a deep zoom image will be 
#  generated for the uploaded image.  Setting it manually got tiresome.
#  Since it's just the default value, it can be overridden programmatically and 
#  manually using the checkbox in the admin.
DEFAULT_CREATE_DEEPZOOM_OPTION = False


#  This logging profile should be added to your project settings to catch any 
#  file handling exceptions.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(TEST_ROOT, 'deepzoom.exception.log'),
        },
    },
    'loggers': {
        'deepzoom.models': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


#EOF django-deepzoom test project settings