#django-deepzoom tests
from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase, SimpleTestCase
from django.db import models, transaction, IntegrityError
from django.template import Template, Context, TemplateSyntaxError
from django.core.files.uploadedfile import SimpleUploadedFile

try:
    from django.utils.text import slugify
except ImportError:
    try:
        from django.template.defaultfilters import slugify
    except ImportError:
        print("Unable to import `slugify`.")

from functools import wraps
import mimetypes as mime
import os, shutil, string

import six

from .utils import is_django_version_greater_than
from .models import UploadedImage, DeepZoom
from .test.models import TestImage

DJANGO_APP_STARTABLE = is_django_version_greater_than(1, 6)

if not DJANGO_APP_STARTABLE:
    from .signals import *



PYTHON2 = six.PY2
PYTHON3 = six.PY3

DEFAULT_UPLOADEDIMAGE_ROOT = UploadedImage.DEFAULT_UPLOADEDIMAGE_ROOT
DEFAULT_DEEPZOOM_ROOT = DeepZoom.DEFAULT_DEEPZOOM_ROOT
VALID_UPLOADEDIMAGE_ROOT = 'images/Uploaded_Images'
VALID_DEEPZOOM_ROOT = 'images/DeepZoom_Images'

BLANK = ''

DEFAULT_DEEPZOOM_PARAMS = DeepZoom.DEFAULT_DEEPZOOM_PARAMS
VALID_DEEPZOOM_PARAMS = {'tile_size': 379,
                         'tile_overlap': 2,
                         'tile_format': "png",
                         'image_quality': 0.9,
                         'resize_filter': "bicubic"}

TEST_FILE_UNKNOWN = 'test_data/test_file.tst'

TEST_IMAGE_INVALID = 'test_data/test_image_INVALID.jpg'

TEST_IMAGE_PORTRAIT = 'test_data/test_img_PORTRAIT.jpg'
TEST_IMAGE_PORTRAIT_WIDTH = 500
TEST_IMAGE_PORTRAIT_HEIGHT = 685

TEST_IMAGE_LANDSCAPE = 'test_data/test_img_LANDSCAPE.jpg'
TEST_IMAGE_LANDSCAPE_WIDTH = 700
TEST_IMAGE_LANDSCAPE_HEIGHT = 522

TEST_IMAGE_SQUARE = 'test_data/test_img_SQUARE.jpg'
TEST_IMAGE_SQUARE_WIDTH = 563
TEST_IMAGE_SQUARE_HEIGHT = 563


'''
    REQUIRED:
        Valid test images located at 'test_data/test_img_PORTRAIT.jpg',and
                                     'test_data/test_img_LANDSCAPE.jpg', and
                                     'test_data/test_img_SQUARE.jpg'.
        
        Dummy test file located at 'test_data/test_file.tst'.
'''

def reSet(_directory=None):
    '''
    Deletes any subdirectories in provided directory while preserving any 
        files, mainly so that test data, if any, can be preserved in media root 
        but test run products saved in subdirectories will be deleted.
    '''
    if os.path.isdir(_directory):
        for _item in os.listdir(_directory):
            _target = os.path.join(_directory, _item)
            if os.path.isdir(_target):
                shutil.rmtree(_target)
            else:
                os.remove(_target)
# /reSet


def max_chars(_num_chars=None):
    '''
    Returns a string of requested size in the form of 
        zero-filled + number-of-characters.
    '''
    return str.zfill(str(_num_chars), _num_chars)
# /max_chars


def simulate_uploaded_file(_read_path=None):
    '''
    Reads a local test file into a SimpleUploadedFile form so that it can be 
        processed by the model-under-test as if it actually had been uploaded.
    '''
    with open(_read_path, 'rb') as _file:
        _content = _file.read()
    _mime = mime.guess_type(_read_path)
    _write_path = settings.MEDIA_ROOT
    _uploaded_file = SimpleUploadedFile(_write_path, _content, _mime)
    return _uploaded_file
# /simulate_uploaded_file


class CreateUpdateImageOnlyTestCase(TestCase):
    '''
    1.) Tests creating an UploadedImage without creating an associated 
        DeepZoom image.
    '''
   
    def test_create_image_without_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.1) Tests UploadedImage creation without settings.UPLOADEDIMAGE_ROOT 
            defined.
        '''
        test_object_name = 'test_img_1.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, DEFAULT_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        img_slug = slugify(six.u(test_img.name))
        self.assertEqual(test_img.slug, img_slug)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertFalse(test_img.create_deepzoom)
        self.assertEqual(test_img.associated_deepzoom, None)
        deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
        self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_image_without_UPLOADEDIMAGE_ROOT_defined
    
    
    def test_create_image_with_blank_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.2) Tests UploadedImage creation with settings.UPLOADEDIMAGE_ROOT 
            defined as a empty string.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = BLANK):
            test_object_name = 'test_img_1.2'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, '')
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_image_with_blank_UPLOADEDIMAGE_ROOT_defined
    
    
    def test_create_image_with_maxchars_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.3) Tests UploadedImage creation with settings.UPLOADEDIMAGE_ROOT 
            defined as a maximum character string.
        '''
        max_char_string = max_chars(255)
        with self.settings(UPLOADEDIMAGE_ROOT = max_char_string):
            test_object_name = 'test_img_1.3'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, max_char_string)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_image_with_maxchars_UPLOADEDIMAGE_ROOT_defined
    
    
    def test_create_landscape_image_with_valid_settings_defined(self):
        '''
        1.4) Tests landscape UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.4'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertTrue(TEST_IMAGE_LANDSCAPE_WIDTH > TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_landscape_image_with_valid_settings_defined
    
    
    def test_create_portrait_image_with_valid_settings_defined(self):
        '''
        1.5) Tests portrait UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.5'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
            self.assertTrue(TEST_IMAGE_PORTRAIT_HEIGHT > TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_portrait_image_with_valid_settings_defined
    
    
    def test_create_square_image_with_valid_settings_defined(self):
        '''
        1.6) Tests portrait UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.6'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertEqual(test_img.height, test_img.width)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    # /test_create_square_image_with_valid_settings_defined
    
    
    def test_create_image_with_invalid_uploaded_image_file(self):
        '''
        1.7) Tests UploadedImage creation with invalid image file uploaded.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.7'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_INVALID)
            image = simulate_uploaded_file(image_path)
            
            with self.assertRaises(TypeError):
                try:
                    with transaction.atomic():
                        test_img = TestImage.objects.create(uploaded_image=image, 
                                                            name=test_object_name)
                except AttributeError:
                    try:
                        test_img = TestImage.objects.create(uploaded_image=image, 
                                                            name=test_object_name)
                    except:
                        raise
            
            img_dir, img_name = TEST_IMAGE_INVALID.split('/')
            img_path = os.path.join(settings.MEDIA_ROOT, VALID_UPLOADEDIMAGE_ROOT)
            img_file = os.path.join(settings.MEDIA_ROOT, VALID_UPLOADEDIMAGE_ROOT, img_name)
            self.assertFalse(os.path.isdir(img_path))
            self.assertFalse(os.path.isfile(img_file))
            dz_path = os.path.join(settings.MEDIA_ROOT, VALID_DEEPZOOM_ROOT, test_object_name)
            dz_file = os.path.join(dz_path, test_object_name + '.dzi')
            self.assertFalse(os.path.isdir(dz_path))
            self.assertFalse(os.path.isfile(dz_file))
        reSet(settings.MEDIA_ROOT)
    # /test_create_image_with_invalid_uploaded_image_file
    
    
    def test_update_image__name__with_valid_settings_defined(self):
        """
        1.8) Tests updated image `name` field.
        """
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.8'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertEqual(test_img.height, test_img.width)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
            
            orig_image_filename = test_img.uploaded_image.name
            new_image_name = 'a new name for an existing image'
            test_img.name = new_image_name
            test_img.save()
            
            #Ensure that updated test image instance is used for next checks...
            new_test_img = TestImage.objects.get(name=new_image_name)
            
            self.assertEqual(new_test_img.name, new_image_name)
            img_slug = slugify(new_test_img.name)
            self.assertEqual(new_test_img.slug, img_slug)
            self.assertEqual(new_test_img.uploaded_image.name, orig_image_filename)
        reSet(settings.MEDIA_ROOT)
    # /test_update_image__name__with_valid_settings_defined
    
    
    def test_update_image__uploaded_image__with_valid_settings_defined(self):
        """
        1.9) Tests updated image `uploaded_image` field (new image file upload).
        """
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.9'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertEqual(test_img.associated_deepzoom, None)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
            
            orig_image_name = test_img.name
            orig_image_slug = test_img.slug
            orig_image_filename = test_img.uploaded_image.name
            orig_height = test_img.height
            orig_width = test_img.width
            new_image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            new_image = simulate_uploaded_file(new_image_path)
            test_img.uploaded_image = new_image
            test_img.save()
            
            #Ensure that updated test image instance is used for next checks...
            new_test_img = TestImage.objects.get(name=orig_image_name)
            
            self.assertEqual(new_test_img.name, orig_image_name)
            img_slug = slugify(six.u(orig_image_name))
            self.assertTrue(new_test_img.slug, orig_image_slug)
            self.assertEqual(new_test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(new_test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(new_test_img.create_deepzoom)
            self.assertEqual(new_test_img.associated_deepzoom, None)
            self.assertTrue(new_test_img.uploaded_image.name == orig_image_filename)
        reSet(settings.MEDIA_ROOT)
    # /test_update_image__uploaded_image__with_valid_settings_defined
    
    
    def suite():
        tests = ['test_create_image_without_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_image_with_blank_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_image_with_maxchars_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_landscape_image_with_valid_settings_defined', 
                 'test_create_portrait_image_with_valid_settings_defined', 
                 'test_create_square_image_with_valid_settings_defined', 
                 'test_create_image_with_invalid_uploaded_image_file', 
                 'test_update_image__name__with_valid_settings_defined', 
                 'test_update_image__uploaded_image__with_valid_settings_defined']

        return unittest.TestSuite(list(map(CreateUpdateImageOnlyTestCase, tests)))
# /CreateUpdateImageOnlyTestCase


class DeleteImageTestCase(TestCase):
    '''
    2.) Class tests deleting UploadedImages singularly and in bulk actions.
    '''
    
    def setUp(self):
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            for num in range(6):
                test_object_name = 'test_img_2.' + str(num)
                image = simulate_uploaded_file(image_path)
                try:
                    TestImage.objects.create(uploaded_image=image, 
                                             name=test_object_name)
                except:
                    raise
        
    
    
    def tearDown(self):
        for test_img in TestImage.objects.all():
            try:
                test_img.delete()
            except:
                raise
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_image_by_calling_delete_method_directly(self):
        '''
        2.1) Tests deleting image by calling delete() method directly.
        '''
        test_object_name = 'test_img_2.1'
        test_img = TestImage.objects.get(name=test_object_name)
        img_path = test_img.uploaded_image.path
        self.assertTrue(os.path.isfile(img_path))
        test_img.delete()
        
        with self.assertRaises(TestImage.DoesNotExist):
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.get(name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.get(name=test_object_name)
                except:
                    raise
        
        self.assertFalse(os.path.exists(img_path))
    # /test_delete_image_by_calling_delete_method_directly
    
    
    def test_delete_image_with_missing_image_file(self):
        '''
        2.2) Tests deleting an image with missing image file.
        '''
        test_object_name = 'test_img_2.2'
        test_img = TestImage.objects.get(name=test_object_name)
        img_path = test_img.uploaded_image.path
        if os.path.isfile(img_path):
            os.remove(img_path)
        test_img.delete()
        
        with self.assertRaises(TestImage.DoesNotExist):
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.get(name=test_object_name)
            except AttributeError:
                try:
                    test_img = TestImage.objects.get(name=test_object_name)
                except:
                    raise
        
        self.assertFalse(os.path.isfile(img_path))
    # /test_delete_image_with_missing_image_file
    
    
    def test_delete_multiple_images_using_bulk_delete_action(self):
        '''
        2.3) Tests deleting multiple images using bulk delete action.
        '''
        test_imgs = TestImage.objects.all()
        img_paths = [test_img.uploaded_image.path for test_img in test_imgs]
        
        for test_img in test_imgs:
            test_img.delete()
            
        for test_img in test_imgs:
            with self.assertRaises(TestImage.DoesNotExist):
                try:
                    with transaction.atomic():
                        TestImage.objects.get(name=test_img.name)
                except AttributeError:
                    try:
                        TestImage.objects.get(name=test_img.name)
                    except:
                        raise
        
        for img_path in img_paths:
            self.assertFalse(os.path.isfile(img_path))
    # /test_delete_multiple_images_using_bulk_delete_action
    
    
    def suite():
        tests = ['test_delete_image_by_calling_delete_method_directly', 
                 'test_delete_image_with_missing_image_file', 
                 'test_delete_multiple_images_using_bulk_delete_action']

        return unittest.TestSuite(list(map(DeleteImageTestCase, tests)))
# /DeleteImageTestCase


class CreateDeepZoomTestCase(TestCase):
    '''
    3.) Class tests creating a DeepZoom image associated with an UploadedImage.
    '''
    
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            try:
                dz.delete()
            except:
                raise
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_without_DEEPZOOM_ROOT_defined(self):
        '''
        3.1) Tests DeepZoom image creation without settings.DEEPZOOM_ROOT defined.
        '''
        test_object_name = 'test_img_3.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        img_slug = slugify(six.u(test_img.name))
        self.assertEqual(test_img.slug, img_slug)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_slug = slugify(test_dz.name)
        self.assertEqual(test_dz.slug, dz_slug)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, DEFAULT_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_without_DEEPZOOM_ROOT_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = '', 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_blank_DEEPZOOM_ROOT_defined(self):
        '''
        3.2) Tests DeepZoom image creation with settings.DEEPZOOM_ROOT defined as
            a blank string.
        '''
        test_object_name = 'test_img_3.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        img_slug = slugify(six.u(test_img.name))
        self.assertEqual(test_img.slug, img_slug)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_slug = slugify(test_dz.name)
        self.assertEqual(test_dz.slug, dz_slug)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, BLANK)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank_DEEPZOOM_ROOT_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = max_chars(255), 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_maxchars_DEEPZOOM_ROOT_defined(self):
        '''
        3.3) Tests DeepZoom image creation with settings.DEEPZOOM_ROOT defined as
            maximum character string.
        '''
        test_object_name = 'test_img_3.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        img_slug = slugify(six.u(test_img.name))
        self.assertEqual(test_img.slug, img_slug)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_slug = slugify(test_dz.name)
        self.assertEqual(test_dz.slug, dz_slug)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        deepzoom_dir, dz_file = os.path.split(test_dz.deepzoom_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        max_dir = max_chars(255)
        self.assertEqual(deepzoom_dir, max_dir)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_maxchars_DEEPZOOM_ROOT_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = DEFAULT_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = '')
    def test_create_deepzoom_with_blank_DEEPZOOM_PARAMS_defined(self):
        '''
        3.4) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            defined.
        '''
        test_object_name = 'test_img_3.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        with self.assertRaises(AttributeError):
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
                except:
                    raise
        
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank_DEEPZOOM_PARAMS_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': '',
                                          'tile_overlap': 10,
                                          'tile_format': "jpg",
                                          'image_quality': 0.15,
                                          'resize_filter': "bicubic"})
    def test_create_deepzoom_with_blank__tile_size__defined(self):
        '''
        3.5.1) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined.
        '''
        test_object_name = 'test_img_3.5.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        with self.assertRaises(ValueError):
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
                except:
                    raise
        
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank__tile_size__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 10001,
                                          'tile_overlap': 9,
                                          'tile_format': "png",
                                          'image_quality': 0.25,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_too_large__tile_size__defined(self):
        '''
        3.5.2) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined with a too-large value.
        '''
        test_object_name = 'test_img_3.5.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_too_large__tile_size__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 256.5,
                                          'tile_overlap': 9,
                                          'tile_format': "png",
                                          'image_quality': 0.35,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_float__tile_size__defined(self):
        '''
        3.5.3) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined as a float value.
        '''
        test_object_name = 'test_img_3.5.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_float__tile_size__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 'string',
                                          'tile_overlap': 9,
                                          'tile_format': "png",
                                          'image_quality': 0.45,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_string__tile_size__defined(self):
        '''
        3.5.4) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        with self.assertRaises(ValueError):
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
                except:
                    raise
        
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_string__tile_size__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 128,
                                          'tile_overlap': "",
                                          'tile_format': "jpg",
                                          'image_quality': 0.55,
                                          'resize_filter': "bilinear"})
    def test_create_deepzoom_with_blank__tile_overlap__defined(self):
        '''
        3.5.5) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined.
        '''
        test_object_name = 'test_img_3.5.5'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        
                
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank__tile_overlap__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 256,
                                          'tile_overlap': -5,
                                          'tile_format': "png",
                                          'image_quality': 0.65,
                                          'resize_filter': "antialias"})
    def test_create_deepzoom_with_negative__tile_overlap__defined(self):
        '''
        3.5.6) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a negative integer value.
        '''
        test_object_name = 'test_img_3.5.6'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_negative__tile_overlap__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 384,
                                          'tile_overlap': 99,
                                          'tile_format': "jpg",
                                          'image_quality': 0.75,
                                          'resize_filter': "bicubic"})
    def test_create_deepzoom_with_too_large__tile_overlap__defined(self):
        '''
        3.5.7) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined with a too-large value.
        '''
        test_object_name = 'test_img_3.5.7'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_too_large__tile_overlap__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 384,
                                          'tile_overlap': 1.5,
                                          'tile_format': "jpg",
                                          'image_quality': 0.85,
                                          'resize_filter': "bicubic"})
    def test_create_deepzoom_with_float__tile_overlap__defined(self):
        '''
        3.5.8) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a float value.
        '''
        test_object_name = 'test_img_3.5.8'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_float__tile_overlap__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 384,
                                          'tile_overlap': "string",
                                          'tile_format': "jpg",
                                          'image_quality': 0.95,
                                          'resize_filter': "bicubic"})
    def test_create_deepzoom_with_string__tile_overlap__defined(self):
        '''
        3.5.9) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.9'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        
        
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_string__tile_overlap__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 512,
                                          'tile_overlap': 8,
                                          'tile_format': "",
                                          'image_quality': 0.94,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_blank__tile_format__defined(self):
        '''
        3.5.10) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined.
        '''
        test_object_name = 'test_img_3.5.10'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank__tile_format__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 500,
                                          'tile_overlap': 7,
                                          'tile_format': "unrecognized",
                                          'image_quality': 0.83,
                                          'resize_filter': "bilinear"})
    def test_create_deepzoom_with_unrecognized__tile_format__defined(self):
        '''
        3.5.11) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined as a unrecognized value.
        '''
        test_object_name = 'test_img_3.5.11'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_unrecognized__tile_format__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 500,
                                          'tile_overlap': 7,
                                          'tile_format': 25,
                                          'image_quality': 0.72,
                                          'resize_filter': "bilinear"})
    def test_create_deepzoom_with_numeric__tile_format__defined(self):
        '''
        3.5.12) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined as a numeric value.
        '''
        test_object_name = 'test_img_3.5.12'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_numeric__tile_format__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 400,
                                          'tile_overlap': 6,
                                          'tile_format': "png",
                                          'image_quality': "",
                                          'resize_filter': "antialias"})
    def test_create_deepzoom_with_blank__image_quality__defined(self):
        '''
        3.5.13) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined.
        '''
        test_object_name = 'test_img_3.5.13'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank__image_quality__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 256.5,
                                          'tile_overlap': 9,
                                          'tile_format': "png",
                                          'image_quality': -0.25,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_negative__image_quality__defined(self):
        '''
        3.5.14) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a negative numeric value.
        '''
        test_object_name = 'test_img_3.5.14'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_negative__image_quality__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 300,
                                          'tile_overlap': 4,
                                          'tile_format': "png",
                                          'image_quality': 9.9,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_too_large__image_quality__defined(self):
        '''
        3.5.15) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined with a too-large numeric value.
        '''
        test_object_name = 'test_img_3.5.15'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_too_large__image_quality__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 200,
                                          'tile_overlap': 7,
                                          'tile_format': "png",
                                          'image_quality': 9,
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_integer__image_quality__defined(self):
        '''
        3.5.16) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a integer value.
        '''
        test_object_name = 'test_img_3.5.16'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_integer__image_quality__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 100,
                                          'tile_overlap': 10,
                                          'tile_format': "png",
                                          'image_quality': "string",
                                          'resize_filter': "nearest"})
    def test_create_deepzoom_with_string__image_quality__defined(self):
        '''
        3.5.17) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.17'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_string__image_quality__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 157,
                                          'tile_overlap': 3,
                                          'tile_format': "jpg",
                                          'image_quality': 0.95,
                                          'resize_filter': ""})
    def test_create_deepzoom_with_blank__resize_filter__defined(self):
        '''
        3.5.18) Tests DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined.
        '''
        test_object_name = 'test_img_3.5.18'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir))) 
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank__resize_filter__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 288,
                                          'tile_overlap': 2,
                                          'tile_format': "png",
                                          'image_quality': 0.9,
                                          'resize_filter': "unrecognized"})
    def test_create_deepzoom_with_unrecognized__resize_filter__defined(self):
        '''
        3.5.19) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined with an unrecognized value.
        '''
        test_object_name = 'test_img_3.5.19'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))  
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_unrecognized__resize_filter__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 311,
                                          'tile_overlap': 7,
                                          'tile_format': "png",
                                          'image_quality': 0.9,
                                          'resize_filter': 2.5})
    def test_create_deepzoom_with_numeric__resize_filter__defined(self):
        '''
        3.5.20) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined as a numeric value.
        '''
        test_object_name = 'test_img_3.5.20'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_numeric__resize_filter__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = {'tile_size': 380,
                                          'tile_overlap': 1,
                                          'tile_format': "png",
                                          'image_quality': 0.5,
                                          'resize_filter': "antialias"})
    def test_create_deepzoom_with_valid_but_not_default_DEEPZOOM_PARAMS(self):
        '''
        3.6) Tests DeepZoom image creation with valid-but-not-default  
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.6'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_valid_but_not_default_DEEPZOOM_PARAMS
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_landscape_deepzoom_with_valid_settings_defined(self):
        '''
        3.7) Tests landscape DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.7'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_landscape_deepzoom_with_valid_settings_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_portrait_deepzoom_with_valid_settings_defined(self):
        '''
        3.8) Tests portrait DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.8'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
        self.assertTrue(test_img.height > test_img.width)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir))) 
        reSet(settings.MEDIA_ROOT)
    # /test_create_portrait_deepzoom_with_valid_settings_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_square_deepzoom_with_valid_settings_defined(self):
        '''
        3.9) Tests square DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.9'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_square_deepzoom_with_valid_settings_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_maxchars__name__defined(self):
        '''
        3.10) Tests DeepZoom image creation with name defined as maximum
            character string.
        '''
        test_object_name = max_chars(64)
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_maxchars__name__defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_without_DEFAULT_CREATE_DEEPZOOM_OPTION_defined(self):
        '''
        3.11) Tests DeepZoom image creation without 
            settings.DEFAULT_CREATE_DEEPZOOM_OPTION defined.
        '''
        test_object_name = 'test_img_11'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_without_DEFAULT_CREATE_DEEPZOOM_OPTION_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = BLANK, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS, 
                       DEFAULT_CREATE_DEEPZOOM_OPTION = None)
    def test_create_deepzoom_with_blank_DEFAULT_CREATE_DEEPZOOM_OPTION_defined(self):
        '''
        3.12) Tests DeepZoom image creation with settings.DEEPZOOM_ROOT defined as
            a blank string.
        '''
        test_object_name = 'test_img_12'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, BLANK)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_blank_DEFAULT_CREATE_DEEPZOOM_OPTION_defined
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS, 
                       DEFAULT_CREATE_DEEPZOOM_OPTION = "non-boolean")
    def test_create_deepzoom_with_non_boolean_DEFAULT_CREATE_DEEPZOOM_OPTION_defined(self):
        '''
        3.13) Tests DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined as a unrecognized value.
        '''
        test_object_name = 'test_img_3.13'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
        except AttributeError:
            try:
                test_img = TestImage.objects.create(uploaded_image=image, 
                                                    name=test_object_name, 
                                                    create_deepzoom=True)
            except:
                raise
        
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
        self.assertTrue(test_img.width < test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        dz_dir, dz_associated_image = os.path.split(test_dz.associated_image)
        img_dir, img_uploaded_image = os.path.split(test_img.uploaded_image.path)
        self.assertEqual(dz_associated_image, img_uploaded_image)
        intermediate_dir, intermediate_file = os.path.split(test_dz.deepzoom_image)
        deepzoom_dir, dz_file = os.path.split(intermediate_dir)
        self.assertEqual(deepzoom_dir, VALID_DEEPZOOM_ROOT)
        self.assertTrue(os.path.isdir(os.path.join(settings.MEDIA_ROOT, 
                                                   deepzoom_dir)))
        reSet(settings.MEDIA_ROOT)
    # /test_create_deepzoom_with_non_boolean_DEFAULT_CREATE_DEEPZOOM_OPTION_defined
    
    
    def test_update_deepzoom_image__name__with_valid_settings_defined(self):
        """
        3.14) Tests updated image `name` field on image and assocaited deepzoom.
        """
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_3.14-(PI!)'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
                except:
                    raise
            
            img_dir, img_file = os.path.split(test_img.uploaded_image.name)
            img_ext = os.path.splitext(img_file)[1]
            self.assertEqual(img_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            test_img_filename = test_img.slug + img_ext
            test_img_path = os.path.join(settings.MEDIA_ROOT, 
                                         settings.UPLOADEDIMAGE_ROOT, 
                                         test_img_filename)
            self.assertEqual(test_img.uploaded_image.path, test_img_path)
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertTrue(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertEqual(test_img.height, test_img.width)
            self.assertFalse(test_img.create_deepzoom)
            
            test_dz1 = test_img.associated_deepzoom
            test_dz2 = DeepZoom.objects.get(name=test_img.name)
            
            self.assertEqual(test_dz1, test_dz2)
            self.assertEqual(test_img.associated_deepzoom, test_dz2)
            self.assertEqual(test_img.name, test_dz1.name)
            self.assertEqual(test_img.slug, test_dz1.slug)
            self.assertEqual(test_img.uploaded_image.name, test_dz1.associated_image)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertTrue(os.path.exists(deepzoom_dir))
            
            orig_image_name = test_img.name
            orig_image_slug = test_img.slug
            orig_image_filename = test_img.uploaded_image.name
            new_image_name = 'a new name for an existing deepzoom'
            orig_deepzoom_name = test_dz1.name
            orig_deepzoom_slug = test_dz1.slug
            orig_deepzoom_path = test_dz1.deepzoom_path
            orig_deepzoom_image = test_dz1.deepzoom_image
            test_img.name = new_image_name
            test_img.save()
            
            #Ensure that updated test image instance is used for next checks...
            new_test_img = TestImage.objects.get(name=new_image_name)
            
            #Ensure that updated test deepzoom instances are used for next checks...
            new_test_dz1 = new_test_img.associated_deepzoom
            new_test_dz2 = DeepZoom.objects.get(name=orig_image_name)
            
            self.assertEqual(new_test_img.name, new_image_name)
            new_test_img_slug = slugify(new_test_img.name)
            self.assertEqual(new_test_img.slug, new_test_img_slug)
            self.assertEqual(new_test_img.width, TEST_IMAGE_SQUARE_WIDTH)
            self.assertEqual(new_test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertEqual(new_test_img.height, new_test_img.width)
            self.assertFalse(new_test_img.create_deepzoom)
            self.assertEqual(new_test_img.uploaded_image.name, orig_image_filename)
            new_img_dir, new_img_file = os.path.split(new_test_img.uploaded_image.name)
            new_img_ext = os.path.splitext(new_img_file)[1]
            new_test_img_filename = orig_image_slug + new_img_ext
            new_test_img_path = os.path.join(settings.MEDIA_ROOT, 
                                             settings.UPLOADEDIMAGE_ROOT, 
                                             new_test_img_filename)
            self.assertEqual(new_test_img.uploaded_image.path, new_test_img_path)
            
            self.assertEqual(new_test_dz1, new_test_dz2)
            self.assertEqual(new_test_img.associated_deepzoom, new_test_dz2)
            self.assertEqual(new_test_dz1.name, orig_image_name)
            self.assertEqual(new_test_dz1.slug, orig_image_slug)
            self.assertEqual(new_test_dz1.associated_image, new_test_img.uploaded_image.name)
            new_dz_dir, new_dz_file = os.path.split(new_test_dz1.deepzoom_image)
            new_dz_ext = os.path.splitext(new_dz_file)[1]
            new_test_dz_filename = orig_deepzoom_slug + new_dz_ext
            new_test_dz_path = os.path.join(settings.DEEPZOOM_ROOT, 
                                            orig_deepzoom_slug)
            new_test_dz_image = os.path.join(new_test_dz_path, 
                                             new_test_dz_filename)
            self.assertEqual(new_test_dz1.deepzoom_path, new_test_dz_path)
            self.assertEqual(new_test_dz1.deepzoom_image, new_test_dz_image)
        reSet(settings.MEDIA_ROOT)
    # /test_update_deepzoom_image__name__with_valid_settings_defined
    
    
    def test_update_image__uploaded_image__with_valid_settings_defined(self):
        """
        3.15) Tests updated image `uploaded_image` field (new image file upload).
        """
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_3.15'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
            image = simulate_uploaded_file(image_path)
            
            try:
                with transaction.atomic():
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
            except AttributeError:
                try:
                    test_img = TestImage.objects.create(uploaded_image=image, 
                                                        name=test_object_name, 
                                                        create_deepzoom=True)
                except:
                    raise
            
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            img_ext = os.path.splitext(img_file)[1]
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            test_img_filename = test_img.slug + img_ext
            test_img_path = os.path.join(settings.MEDIA_ROOT, 
                                         settings.UPLOADEDIMAGE_ROOT, 
                                         test_img_filename)
            self.assertEqual(test_img.uploaded_image.path, test_img_path)
            self.assertEqual(test_img.name, test_object_name)
            img_slug = slugify(six.u(test_img.name))
            self.assertEqual(test_img.slug, img_slug)
            self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            
            test_dz1 = test_img.associated_deepzoom
            test_dz2 = DeepZoom.objects.get(name=test_img.name)
            
            self.assertEqual(test_dz1, test_dz2)
            self.assertEqual(test_img.associated_deepzoom, test_dz2)
            self.assertEqual(test_img.name, test_dz1.name)
            self.assertEqual(test_img.slug, test_dz1.slug)
            self.assertEqual(test_img.uploaded_image.name, test_dz1.associated_image)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertTrue(os.path.exists(deepzoom_dir))
            
            orig_image_name = test_img.name
            orig_image_slug = test_img.slug
            orig_image_filename = test_img.uploaded_image.name
            orig_height = test_img.height
            orig_width = test_img.width
            orig_deepzoom_name = test_dz1.name
            orig_deepzoom_slug = test_dz1.slug
            orig_deepzoom_path = test_dz1.deepzoom_path
            orig_deepzoom_image = test_dz1.deepzoom_image
            new_image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            new_image = simulate_uploaded_file(new_image_path)
            test_img.uploaded_image = new_image
            test_img.create_deepzoom = True
            test_img.save()
            
            #Ensure that updated test image instance is used for next checks...
            new_test_img = TestImage.objects.get(name=orig_image_name)
            
            #Ensure that updated test deepzoom instances are used for next checks...
            new_test_dz1 = new_test_img.associated_deepzoom
            new_test_dz2 = DeepZoom.objects.get(name=new_test_img.name)
            
            self.assertEqual(new_test_img.name, orig_image_name)
            self.assertEqual(new_test_img.slug, orig_image_slug)
            self.assertEqual(new_test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(new_test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(new_test_img.create_deepzoom)
            self.assertEqual(new_test_img.associated_deepzoom, new_test_dz2)
            new_img_dir, new_img_file = os.path.split(new_test_img.uploaded_image.name)
            new_img_ext = os.path.splitext(new_img_file)[1]
            new_test_img_filename = new_test_img.slug + new_img_ext
            new_test_img_path = os.path.join(settings.MEDIA_ROOT, 
                                             settings.UPLOADEDIMAGE_ROOT, 
                                             new_test_img_filename)
            self.assertEqual(new_test_img.uploaded_image.path, new_test_img_path)
            self.assertEqual(new_test_dz1, new_test_dz2)
            self.assertEqual(new_test_img.associated_deepzoom, new_test_dz2)
            self.assertEqual(new_test_dz1.name, orig_image_name)
            self.assertEqual(new_test_dz1.slug, orig_image_slug)
            self.assertEqual(new_test_dz1.associated_image, new_test_img.uploaded_image.name)
            new_dz_dir, new_dz_file = os.path.split(new_test_dz1.deepzoom_image)
            new_dz_ext = os.path.splitext(new_dz_file)[1]
            new_test_dz_slug = slugify(new_test_dz1.name)
            new_test_dz_filename = new_test_dz_slug + new_dz_ext
            new_test_dz_path = os.path.join(settings.DEEPZOOM_ROOT, 
                                            new_test_dz1.slug)
            new_test_dz_image = os.path.join(new_test_dz_path, 
                                             new_test_dz_filename)
            self.assertEqual(new_test_dz1.deepzoom_path, new_test_dz_path)
            self.assertEqual(new_test_dz1.deepzoom_image, new_test_dz_image)
        reSet(settings.MEDIA_ROOT)
    # /test_update_image__uploaded_image__with_valid_settings_defined
    
    
    def suite():
        tests = ['test_create_deepzoom_without_DEEPZOOM_ROOT_defined', 
                 'test_create_deepzoom_with_blank_DEEPZOOM_ROOT_defined', 
                 'test_create_deepzoom_with_maxchars_DEEPZOOM_ROOT_defined', 
                 'test_create_deepzoom_with_blank_DEEPZOOM_PARAMS_defined', 
                 'test_create_deepzoom_with_blank__tile_size__defined', 
                 'test_create_deepzoom_with_too_large__tile_size__defined', 
                 'test_create_deepzoom_with_float__tile_size__defined', 
                 'test_create_deepzoom_with_string__tile_size__defined', 
                 'test_create_deepzoom_with_blank__tile_overlap__defined', 
                 'test_create_deepzoom_with_negative__tile_overlap__defined', 
                 'test_create_deepzoom_with_too_large__tile_overlap__defined', 
                 'test_create_deepzoom_with_float__tile_overlap__defined', 
                 'test_create_deepzoom_with_string__tile_overlap__defined', 
                 'test_create_deepzoom_with_blank__tile_format__defined', 
                 'test_create_deepzoom_with_unrecognized__tile_format__defined', 
                 'test_create_deepzoom_with_numeric__tile_format__defined', 
                 'test_create_deepzoom_with_blank__image_quality__defined', 
                 'test_create_deepzoom_with_negative__image_quality__defined', 
                 'test_create_deepzoom_with_too_large__image_quality__defined', 
                 'test_create_deepzoom_with_integer__image_quality__defined', 
                 'test_create_deepzoom_with_string__image_quality__defined', 
                 'test_create_deepzoom_with_blank__resize_filter__defined', 
                 'test_create_deepzoom_with_unrecognized__resize_filter__defined', 
                 'test_create_deepzoom_with_numeric__resize_filter__defined', 
                 'test_create_deepzoom_with_valid_but_not_default_DEEPZOOM_PARAMS', 
                 'test_create_landscape_deepzoom_with_valid_settings_defined', 
                 'test_create_portrait_deepzoom_with_valid_settings_defined', 
                 'test_create_square_deepzoom_with_valid_settings_defined', 
                 'test_create_deepzoom_with_maxchars__name__defined', 
                 'test_update_deepzoom_image__name__with_valid_settings_defined']

        return unittest.TestSuite(list(map(CreateDeepZoomTestCase, tests)))
# /CreateDeepZoomTestCase


@override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                   DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                   DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
class DeleteDeepZoomTestCase(TestCase):
    '''
    4.) Class tests deleting DeepZooms singularly and in bulk actions.
    '''
    def setUp(self):
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        for num in range(6):
            self.test_object_name = 'test_dz_4.' + str(num)
            image = simulate_uploaded_file(image_path)
            try:
                TestImage.objects.create(uploaded_image=image, 
                                         name=self.test_object_name, 
                                         create_deepzoom=True)
            except:
                raise
    
    
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            try:
                dz.delete()
            except:
                raise
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_deepzoom_by_calling_delete_method_directly(self):
        '''
        4.1) Tests deleting DeepZoom by calling delete() method directly.
        '''
        test_object_name = 'test_dz_4.3'
        test_dz = DeepZoom.objects.get(name=test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        
        try:
            with transaction.atomic():
                test_dz.delete()
        except AttributeError:
            try:
                test_dz.delete()
            except:
                raise
        
        with self.assertRaises(DeepZoom.DoesNotExist):
            try:
                with transaction.atomic():
                    test_dz = DeepZoom.objects.get(name=test_object_name)
            except AttributeError:
                try:
                    test_dz = DeepZoom.objects.get(name=test_object_name)
                except:
                    raise
                
        self.assertFalse(os.path.isdir(dz_path))
        self.assertFalse(os.path.isfile(dz_file))
        reSet(settings.MEDIA_ROOT)
    # /test_delete_deepzoom_by_calling_delete_method_directly
    
    
    def test_delete_deepzoom_with_missing_dzi_files(self):
        '''
        4.2) Tests attempt to delete DeepZoom with missing deep zoom image files.
        '''
        test_object_name = 'test_dz_4.2'
        test_dz = DeepZoom.objects.get(name=test_object_name)
        dz_path = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
        self.assertTrue(os.path.isdir(dz_path))
        
        if os.path.isdir(dz_path):
            shutil.rmtree(dz_path)
        
        try:
            with transaction.atomic():
                test_dz.delete()
        except AttributeError:
            try:
                test_dz.delete()
            except:
                raise
                
        with self.assertRaises(DeepZoom.DoesNotExist):
            try:
                with transaction.atomic():
                    test_dz = DeepZoom.objects.get(name=test_object_name)
            except AttributeError:
                try:
                    test_dz = DeepZoom.objects.get(name=test_object_name)
                except:
                    raise
        
        self.assertFalse(os.path.isdir(dz_path))
        reSet(settings.MEDIA_ROOT)
    # /test_delete_deepzoom_with_missing_dzi_files
    
    
    def test_delete_all_deepzooms_using_bulk_delete_action(self):
        '''
        4.3) Tests deleting multiple deep zoom images using bulk delete action.
        '''
        test_dzs = DeepZoom.objects.all()
        dz_paths = [os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_path)
                    for test_dz in test_dzs]
        
        for dz_path in dz_paths:
            self.assertTrue(os.path.isdir(dz_path))
        
        for test_dz in test_dzs:
            try:
                test_dz.delete()
            except:
                raise
        
        for test_dz in test_dzs:
            with self.assertRaises(DeepZoom.DoesNotExist):
                try:
                    with transaction.atomic():
                        DeepZoom.objects.get(name=test_dz.name)
                except AttributeError:
                    try:
                        DeepZoom.objects.get(name=test_dz.name)
                    except:
                        raise
        
        for dz_path in dz_paths:
            self.assertFalse(os.path.isdir(dz_path))
        
        reSet(settings.MEDIA_ROOT)
    # /test_delete_all_deepzooms_using_bulk_delete_action
    
    
    def suite():
        tests = ['delete_deepzoom_by_calling_delete_method_directly', 
                 'delete_deepzoom_with_missing_dzi_files', 
                 'delete_all_deepzooms_using_bulk_delete_action']

        return unittest.TestSuite(list(map(DeleteDeepZoomTestCase, tests)))
# /DeleteDeepZoomTestCase


@override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                   DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                   DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
class DeepZoomFirstTemplateTagTestCase(SimpleTestCase):
    '''
    5.) Class tests DeepZoom JavaScript inclusion template tag.
    '''
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            try:
                dz.delete()
            except:
                raise
        reSet(settings.MEDIA_ROOT)
    
    
    def test_call_template_tag_without_deepzoom_object(self):
        '''
        5.1) Tests calling deepzoom_js template tag without first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_5.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        if PYTHON2:
            except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        elif PYTHON3:
            except_string = "The 'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    # /test_call_template_tag_without_deepzoom_object
    
    
    def test_call_template_tag_without__deep_zoom_div_id__argument(self):
        '''
        5.2) Tests calling deepzoom_js template tag without second 
            (Deep Zoom div ID) argument.
        '''
        test_object_name = 'test_dz_5.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        if PYTHON2:
            except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        elif PYTHON3:
            except_string = "The 'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    # /test_call_template_tag_without__deep_zoom_div_id__argument
    
    
    def test_call_template_tag_with_extra_argument(self):
        '''
        5.3) Tests calling deepzoom_js template tag with extra argument.
        '''
        test_object_name = 'test_dz_5.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        if PYTHON2:
            except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        elif PYTHON3:
            except_string = "The 'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj 'deepzoom_div' extra %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    # /test_call_template_tag_with_extra_argument
    
    
    def test_call_template_tag_with_first_argument_quoted(self):
        '''
        5.4) Tests calling deepzoom_js template tag with quoted first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_5.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        if PYTHON2:
            except_string = "The u'deepzoom_js' tag's 'Deep Zoom object' argument should not be in quotes."
        elif PYTHON3:
            except_string = "The 'deepzoom_js' tag's 'Deep Zoom object' argument should not be in quotes."
        
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js 'deepzoom_obj' 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    # /test_call_template_tag_with_first_argument_quoted
    
    
    def test_call_template_tag_with_unquoted__deep_zoom_div_id__argument(self):
        '''
        5.5) Tests calling deepzoom_js template tag with unquoted second 
            (Deep Zoom div ID) argument.
        '''
        test_object_name = 'test_dz_5.5'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        if PYTHON2:
            except_string = "The u'deepzoom_js' tag's 'Deep Zoom div ID' argument should be in quotes."
        elif PYTHON3:
            except_string = "The 'deepzoom_js' tag's 'Deep Zoom div ID' argument should be in quotes."
        
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj deepzoom_div %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    # /test_call_template_tag_with_unquoted__deep_zoom_div_id__argument
    
    
    def suite():
        tests = ['test_call_template_tag_without_deepzoom_object', 
                 'test_call_template_tag_without__deep_zoom_div_id__argument', 
                 'test_call_template_tag_with_extra_argument', 
                 'test_call_template_tag_with_first_argument_quoted', 
                 'test_call_template_tag_with_unquoted__deep_zoom_div_id__argument']

        return unittest.TestSuite(list(map(DeepZoomFirstTemplateTagTestCase, tests)))
# /DeepZoomFirstTemplateTagTestCase


@override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
               DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
               DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
class DeepZoomSecondTemplateTagTestCase(TestCase):
    '''
    6.) Class tests DeepZoom JavaScript inclusion template tag.
    '''
    def test_call_template_tag_with_first_argument_unrecognized_object(self):
        '''
        6.1) Tests calling deepzoom_js template tag with unrecognized first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_6.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        out = Template("{% load deepzoom_tags %}"
                       "{% deepzoom_js unknown_obj 'deepzoom_div' %}"
                       ).render(Context({'deepzoom_obj': test_dz}))
        
        self.assertEqual(out, "")
    # /test_call_template_tag_with_first_argument_unrecognized_object
    
    
    def test_call_template_tag_with_correct_number_and_format_arguments(self):
        '''
        6.2) Tests calling deepzoom_js template tag with correct number and 
            format of arguments.
        '''
        test_object_name = 'test_dz_6.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        
        try:
            with transaction.atomic():
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
        except AttributeError:
            try:
                test_dz = TestImage.objects.create(uploaded_image=image, 
                                                   name=test_object_name, 
                                                   create_deepzoom=True)
            except:
                raise
        
        with self.assertTemplateUsed('deepzoom/deepzoom_js.html'):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
            
            self.assertNotEqual(out, "")
    # /test_call_template_tag_with_correct_number_and_format_arguments
    
    
    def suite():
        tests = ['test_call_template_tag_with_first_argument_unrecognized_object', 
                 'test_call_template_tag_with_correct_number_and_format_arguments']

        return unittest.TestSuite(list(map(DeepZoomSecondTemplateTagTestCase, tests)))
# /DeepZoomSecondTemplateTagTestCase


#EOF - django-deepzoom tests