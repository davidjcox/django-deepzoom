#django-deepzoom tests
from django.test import TestCase, SimpleTestCase
from django.db import models
from django.conf import settings
from django.db import IntegrityError
from django.test.utils import override_settings
from django.template import Template, Context, TemplateSyntaxError
from django.core.files.uploadedfile import SimpleUploadedFile

from functools import wraps
import mimetypes as mime
import os, shutil, string


from .models import TestImage, UploadedImage, DeepZoom


DEFAULT_UPLOADEDIMAGE_ROOT = UploadedImage.DEFAULT_UPLOADEDIMAGE_ROOT
DEFAULT_DEEPZOOM_ROOT = DeepZoom.DEFAULT_DEEPZOOM_ROOT
VALID_UPLOADEDIMAGE_ROOT = 'images/Uploaded_Images'
VALID_DEEPZOOM_ROOT = 'images/DeepZoom_Images'

BLANK = ''

DEFAULT_DEEPZOOM_PARAMS = DeepZoom.DEFAULT_DEEPZOOM_PARAMS
VALID_DEEPZOOM_PARAMS = ['379', 2, 'png', 0.9, 'bicubic']

TEST_FILE_UNKNOWN = 'test_data/test_file.tst'

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
    Deletes any directories residing in provided directory while preserving any 
        files, mainly so that test data, if any, can be preserved in media root 
        but test run products saved in child directories will be deleted.
    '''
    if os.listdir(_directory):
        for _item in os.listdir(_directory):
            _target = os.path.join(_directory, _item)
            if os.path.isdir(_target):
                shutil.rmtree(_target)
            else:
                os.remove(_target)
#end reSet


def identify_self(f):
    '''
    Decorator that exposes name of wrapped function as 'self.__name__' to 
        that function.
    '''
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(f, *args, **kwargs)
    return wrapper
#end identify_self decorator


def max_chars(_num_chars=None):
    '''
    Returns a string of requested size in the form of 
        zero-filled + number-of-characters.
    '''
    return string.zfill(_num_chars, _num_chars)
#end max_chars


def simulate_uploaded_file(_path=None):
    '''
    Reads a local test file into a SimpleUploadedFile form so that it can be 
        processed by the model-under-test as if it actually had been uploaded.
    '''
    _file = open(_path)
    _content = _file.read()
    _file.close()
    _mime = mime.guess_type(_path)
    _uploaded_file = SimpleUploadedFile(_path, _content, _mime)
    return _uploaded_file
#end simulate_uploaded_file


class CreateImageOnlyTestCase(TestCase):
    '''
    1.) Class tests creating an UploadedImage without creating an associated 
        DeepZoom image.
    '''
   
    def test_create_image_without_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.1) Test UploadedImage creation without settings.UPLOADEDIMAGE_ROOT 
            defined.
        '''
        test_object_name = 'test_img_1.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, DEFAULT_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertFalse(test_img.create_deepzoom)
        self.assertFalse(test_img.deepzoom_already_created)
        #self.assertIsNone(test_img.associated_deepzoom)
        deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
        self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    
    
    def test_create_image_with_blank_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.2) Test UploadedImage creation with settings.UPLOADEDIMAGE_ROOT 
            defined as a empty string.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = ''):
            test_object_name = 'test_img_1.2'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, '')
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertFalse(test_img.deepzoom_already_created)
            #self.assertIsNone(test_img.associated_deepzoom)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    
    
    def test_create_image_with_maxchars_UPLOADEDIMAGE_ROOT_defined(self):
        '''
        1.3) Test UploadedImage creation with settings.UPLOADEDIMAGE_ROOT 
            defined as a maximum character string.
        '''
        max_char_string = max_chars(255)
        with self.settings(UPLOADEDIMAGE_ROOT = max_char_string):
            test_object_name = 'test_img_1.3'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, max_char_string)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertFalse(test_img.deepzoom_already_created)
            #self.assertIsNone(test_img.associated_deepzoom)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    
    
    def test_create_image_with_duplicate__name__defined(self):
        '''
        1.4) Test attempt to create an UploadedImage with a duplicate name.
        '''
        test_object_name = 'test_img_1.4'
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            test_img1 = TestImage.objects.create(uploaded_image=image, 
                                                 name=test_object_name)
            with self.assertRaises(IntegrityError):
                test_img2 = TestImage.objects.create(uploaded_image=image, 
                                                     name=test_object_name)
        reSet(settings.MEDIA_ROOT)
    
    
    def test_create_landscape_image_with_valid_settings_defined(self):
        '''
        1.5) Test landscape UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.5'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
            image = simulate_uploaded_file(image_path)
            test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertTrue(TEST_IMAGE_LANDSCAPE_WIDTH > TEST_IMAGE_LANDSCAPE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertFalse(test_img.deepzoom_already_created)
            #self.assertIsNone(test_img.associated_deepzoom)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    

    def test_create_portrait_image_with_valid_settings_defined(self):
        '''
        1.6) Test portrait UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.6'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
            image = simulate_uploaded_file(image_path)
            test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
            self.assertTrue(TEST_IMAGE_PORTRAIT_HEIGHT > TEST_IMAGE_PORTRAIT_WIDTH)
            self.assertFalse(test_img.create_deepzoom)
            self.assertFalse(test_img.deepzoom_already_created)
            #self.assertIsNone(test_img.associated_deepzoom)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    

    def test_create_square_image_with_valid_settings_defined(self):
        '''
        1.7) Test portrait UploadedImage creation with all valid settings.
        '''
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            test_object_name = 'test_img_1.7'
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            image = simulate_uploaded_file(image_path)
            test_img = TestImage.objects.create(uploaded_image=image, 
                                                name=test_object_name)
            media_dir, img_file = os.path.split(test_img.uploaded_image.name)
            self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
            self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
            self.assertEqual(test_img.name, test_object_name)
            self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
            self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertEqual(TEST_IMAGE_SQUARE_WIDTH, TEST_IMAGE_SQUARE_HEIGHT)
            self.assertFalse(test_img.create_deepzoom)
            self.assertFalse(test_img.deepzoom_already_created)
            #self.assertIsNone(test_img.associated_deepzoom)
            deepzoom_dir = os.path.join(settings.MEDIA_ROOT, DEFAULT_DEEPZOOM_ROOT)
            self.assertFalse(os.path.exists(deepzoom_dir))
        reSet(settings.MEDIA_ROOT)
    
    
    def suite():
        tests = ['test_create_image_without_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_image_with_blank_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_image_with_maxchars_UPLOADEDIMAGE_ROOT_defined', 
                 'test_create_image_with_duplicate__name__defined', 
                 'test_create_image_with_unrecognized_image_file', 
                 'test_create_landscape_image_with_valid_settings_defined', 
                 'test_create_portrait_image_with_valid_settings_defined', 
                 'test_create_square_image_with_valid_settings_defined']

        return unittest.TestSuite(map(CreateImageOnlyTestCase, tests))
# #end CreateImageOnlyTestCase


class DeleteImageTestCase(TestCase):
    '''
    2.) Class tests deleting UploadedImages singularly and in bulk actions.
    '''
    
    def setUp(self):
        with self.settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT):
            image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
            for num in range(6):
                self.test_object_name = 'test_img_2.' + str(num)
                image = simulate_uploaded_file(image_path)
                TestImage.objects.create(uploaded_image=image, 
                                         name=self.test_object_name)
    
    
    def tearDown(self):
        for test_img in TestImage.objects.all():
            test_img.delete()
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_image_by_calling_delete_method_directly(self):
        '''
        2.1) Test deleting image by calling delete() method directly.
        '''
        test_object_name = 'test_img_2.2'
        test_img = TestImage.objects.get(name=test_object_name)
        img_path = test_img.uploaded_image.path
        self.assertTrue(os.path.isfile(img_path))
        test_img.delete()
        with self.assertRaises(TestImage.DoesNotExist):
            test_img = TestImage.objects.get(name=test_object_name)
        self.assertFalse(os.path.isfile(img_path))
    
    
    def test_delete_image_with_missing_image_file(self):
        '''
        2.2) Test deleting an image with missing image file.
        '''
        test_object_name = 'test_img_2.5'
        test_img = TestImage.objects.get(name=test_object_name)
        img_path = test_img.uploaded_image.path
        if os.path.isfile(img_path):
            os.remove(img_path)
        test_img.delete()
        with self.assertRaises(TestImage.DoesNotExist):
            test_img = TestImage.objects.get(name=test_object_name)
        self.assertFalse(os.path.isfile(img_path))
    
    
    def test_delete_multiple_images_using_bulk_delete_action(self):
        '''
        2.3) Test deleting multiple images using bulk delete action.
        '''
        test_imgs = TestImage.objects.all()
        img_paths = [test_img.uploaded_image.path for test_img in test_imgs]
        for test_img in test_imgs:
            test_img.delete()
        for test_img in test_imgs:
            with self.assertRaises(TestImage.DoesNotExist):
                TestImage.objects.get(name=test_img.name)
        for img_path in img_paths:
            self.assertFalse(os.path.isfile(img_path))
    
    
    def suite():
        tests = ['test_delete_image_by_calling_delete_method_directly', 
                 'test_delete_image_with_missing_image_file', 
                 'test_delete_multiple_images_using_bulk_delete_action']

        return unittest.TestSuite(map(DeleteImageTestCase, tests))
#end DeleteImageTestCase


class CreateDeepZoomTestCase(TestCase):
    '''
    3.) Class tests creating a DeepZoom image associated with an UploadedImage.
    '''
    
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            dz.delete()
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_without_DEEPZOOM_ROOT_defined(self):
        '''
        3.1) Test DeepZoom image creation without settings.DEEPZOOM_ROOT defined.
        '''
        test_object_name = 'test_img_3.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = '', 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_blank_DEEPZOOM_ROOT_defined(self):
        '''
        3.2) Test DeepZoom image creation with settings.DEEPZOOM_ROOT defined as
            a blank string.
        '''
        test_object_name = 'test_img_3.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = max_chars(255), 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_maxchars_DEEPZOOM_ROOT_defined(self):
        '''
        3.3) Test DeepZoom image creation with settings.DEEPZOOM_ROOT defined as
            maximum character string.
        '''
        test_object_name = 'test_img_3.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = DEFAULT_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = '')
    def test_create_deepzoom_with_blank_DEEPZOOM_PARAMS_defined(self):
        '''
        3.4) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            defined.
        '''
        test_object_name = 'test_img_3.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = ['', 10, 'jpg', 0.15, 'bicubic'])
    def test_create_deepzoom_with_blank__tile_size__defined(self):
        '''
        3.5.1) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined.
        '''
        test_object_name = 'test_img_3.5.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertFalse(test_img.deepzoom_already_created)
        #self.assertIsNone(test_img.associated_deepzoom)
        with self.assertRaises(DeepZoom.DoesNotExist):
            DeepZoom.objects.get(name=test_object_name)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [10001, 9, 'png', 0.25, 'nearest'])
    def test_create_deepzoom_with_too_large__tile_size__defined(self):
        '''
        3.5.2) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined with a too-large value.
        '''
        test_object_name = 'test_img_3.5.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [256.5, 9, 'png', 0.35, 'nearest'])
    def test_create_deepzoom_with_float__tile_size__defined(self):
        '''
        3.5.3) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined as a float value.
        '''
        test_object_name = 'test_img_3.5.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = ['string', 9, 'png', 0.45, 'nearest'])
    def test_create_deepzoom_with_string__tile_size__defined(self):
        '''
        3.5.4) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_size' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertFalse(test_img.deepzoom_already_created)
        #self.assertIsNone(test_img.associated_deepzoom)
        with self.assertRaises(DeepZoom.DoesNotExist):
            DeepZoom.objects.get(name=test_object_name)
        reSet(settings.MEDIA_ROOT)
    
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [128, '', 'jpg', 0.55, 'bilinear'])
    def test_create_deepzoom_with_blank__tile_overlap__defined(self):
        '''
        3.5.5) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined.
        '''
        test_object_name = 'test_img_3.5.5'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertFalse(test_img.deepzoom_already_created)
        #self.assertIsNone(test_img.associated_deepzoom)
        with self.assertRaises(DeepZoom.DoesNotExist):
            DeepZoom.objects.get(name=test_object_name)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [256, -5, 'png', 0.65, 'antialias'])
    def test_create_deepzoom_with_negative__tile_overlap__defined(self):
        '''
        3.5.6) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a negative integer value.
        '''
        test_object_name = 'test_img_3.5.6'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [384, 99, 'jpg', 0.75, 'bicubic'])
    def test_create_deepzoom_with_too_large__tile_overlap__defined(self):
        '''
        3.5.7) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined with a too-large value.
        '''
        test_object_name = 'test_img_3.5.7'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [384, 1.5, 'jpg', 0.85, 'bicubic'])
    def test_create_deepzoom_with_float__tile_overlap__defined(self):
        '''
        3.5.8) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a float value.
        '''
        test_object_name = 'test_img_3.5.8'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [384, 'string', 'jpg', 0.95, 'bicubic'])
    def test_create_deepzoom_with_string__tile_overlap__defined(self):
        '''
        3.5.9) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_overlap' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.9'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        test_img.full_clean()
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertFalse(test_img.deepzoom_already_created)
        #self.assertIsNone(test_img.associated_deepzoom)
        with self.assertRaises(DeepZoom.DoesNotExist):
            DeepZoom.objects.get(name=test_object_name)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [512, 8, '', 0.94, 'nearest'])
    def test_create_deepzoom_with_blank__tile_format__defined(self):
        '''
        3.5.10) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined.
        '''
        test_object_name = 'test_img_3.5.10'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [500, 7, 'unrecognized', 0.83, 'bilinear'])
    def test_create_deepzoom_with_unrecognized__tile_format__defined(self):
        '''
        3.5.11) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined as a unrecognized value.
        '''
        test_object_name = 'test_img_3.5.11'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [500, 7, 25, 0.72, 'bilinear'])
    def test_create_deepzoom_with_numeric__tile_format__defined(self):
        '''
        3.5.12) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'tile_format' parameter defined as a numeric value.
        '''
        test_object_name = 'test_img_3.5.12'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [400, 6, 'png', '', 'antialias'])
    def test_create_deepzoom_with_blank__image_quality__defined(self):
        '''
        3.5.13) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined.
        '''
        test_object_name = 'test_img_3.5.13'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [256.5, 9, 'png', -0.25, 'nearest'])
    def test_create_deepzoom_with_negative__image_quality__defined(self):
        '''
        3.5.14) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a negative numeric value.
        '''
        test_object_name = 'test_img_3.5.14'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [300, 4, 'png', 9.9, 'nearest'])
    def test_create_deepzoom_with_too_large__image_quality__defined(self):
        '''
        3.5.15) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined with a too-large numeric value.
        '''
        test_object_name = 'test_img_3.5.15'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [200, 7, 'png', 9, 'nearest'])
    def test_create_deepzoom_with_integer__image_quality__defined(self):
        '''
        3.5.16) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a integer value.
        '''
        test_object_name = 'test_img_3.5.16'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [100, 10, 'png', 'string', 'nearest'])
    def test_create_deepzoom_with_string__image_quality__defined(self):
        '''
        3.5.17) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'image_quality' parameter defined as a string value.
        '''
        test_object_name = 'test_img_3.5.17'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [157, 3, 'jpg', 0.95, ''])
    def test_create_deepzoom_with_blank__resize_filter__defined(self):
        '''
        3.5.18) Test DeepZoom image creation with blank settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined.
        '''
        test_object_name = 'test_img_3.5.18'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [288, 2, 'png', 0.9, 'unrecognized'])
    def test_create_deepzoom_with_unrecognized__resize_filter__defined(self):
        '''
        3.5.19) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined with an unrecognized value.
        '''
        test_object_name = 'test_img_3.5.19'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = [311, 7, 'png', 0.9, 2.5])
    def test_create_deepzoom_with_numeric__resize_filter__defined(self):
        '''
        3.5.20) Test DeepZoom image creation with settings.DEEPZOOM_PARAMS 
            'resize_filter' parameter defined as a numeric value.
        '''
        test_object_name = 'test_img_3.5.20'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = ['380', 1, 'png', 0.5, 'antialias'])
    def test_create_deepzoom_with_valid_but_not_default_DEEPZOOM_PARAMS(self):
        '''
        3.6) Test DeepZoom image creation with valid-but-not-default  
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.6'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_duplicate__name__defined(self):
        '''
        3.7) Test attempt to create DeepZoom image with duplicate name.
        '''
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        self.test_object_name = 'test_img_3.7.1'
        test_img1 = TestImage.objects.create(uploaded_image=image, 
                                             name=self.test_object_name, 
                                             create_deepzoom=True)
        self.test_object_name = 'test_img_3.7.2'
        test_img2 = TestImage.objects.create(uploaded_image=image, 
                                             name=self.test_object_name, 
                                             create_deepzoom=False)
        with self.assertRaises(IntegrityError):
            test_dz2 = DeepZoom(associated_image=test_img2.uploaded_image.path, 
                                name=test_img1.name)
            test_dz2.save()
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_landscape_deepzoom_with_valid_settings_defined(self):
        '''
        3.8) Test landscape DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.8'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_LANDSCAPE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_LANDSCAPE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_LANDSCAPE_HEIGHT)
        self.assertTrue(test_img.width > test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_portrait_deepzoom_with_valid_settings_defined(self):
        '''
        3.9) Test portrait DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.9'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_PORTRAIT_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_PORTRAIT_HEIGHT)
        self.assertTrue(test_img.height > test_img.width)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
        
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_square_deepzoom_with_valid_settings_defined(self):
        '''
        3.10) Test square DeepZoom image creation with valid   
            settings.DEEPZOOM_PARAMS parameters defined.
        '''
        test_object_name = 'test_img_3.10'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
    @override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                       DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                       DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
    def test_create_deepzoom_with_maxchars__name__defined(self):
        '''
        3.11) Test DeepZoom image creation with name defined as maximum
            character string.
        '''
        test_object_name = max_chars(64)
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_SQUARE)
        image = simulate_uploaded_file(image_path)
        test_img = TestImage.objects.create(uploaded_image=image, 
                                            name=test_object_name, 
                                            create_deepzoom=True)
        media_dir, img_file = os.path.split(test_img.uploaded_image.name)
        self.assertEqual(media_dir, VALID_UPLOADEDIMAGE_ROOT)
        self.assertTrue(os.path.isfile(test_img.uploaded_image.path))
        self.assertEqual(test_img.name, test_object_name)
        self.assertEqual(test_img.width, TEST_IMAGE_SQUARE_WIDTH)
        self.assertEqual(test_img.height, TEST_IMAGE_SQUARE_HEIGHT)
        self.assertTrue(test_img.width == test_img.height)
        self.assertFalse(test_img.create_deepzoom)
        self.assertTrue(test_img.deepzoom_already_created)
        #self.assertIsNotNone(test_img.associated_deepzoom)
        test_dz = DeepZoom.objects.get(name=test_object_name)
        #self.assertEqual(test_img.associated_deepzoom, test_dz)
        self.assertEqual(test_dz.name, test_object_name)
        dz_path = test_dz.deepzoom_path
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
        self.assertIsNotNone(test_dz.deepzoom_xml)
        reSet(settings.MEDIA_ROOT)
    
    
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
                 'test_create_deepzoom_with_duplicate__name__defined', 
                 'test_create_landscape_deepzoom_with_valid_settings_defined', 
                 'test_create_portrait_deepzoom_with_valid_settings_defined', 
                 'test_create_square_deepzoom_with_valid_settings_defined', 
                 'test_create_deepzoom_with_maxchars__name__defined']

        return unittest.TestSuite(map(CreateDeepZoomTestCase, tests))
#end CreateDeepZoomTestCase


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
            TestImage.objects.create(uploaded_image=image, 
                                     name=self.test_object_name, 
                                     create_deepzoom=True)
    
    
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            dz.delete()
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_deepzoom_by_calling_delete_method_directly(self):
        '''
        4.1) Test deleting DeepZoom by calling delete() method directly.
        '''
        test_object_name = 'test_dz_4.3'
        test_dz = DeepZoom.objects.get(name=test_object_name)
        dz_path = test_dz.deepzoom_path
        dz_file = os.path.join(settings.MEDIA_ROOT, test_dz.deepzoom_image)
        self.assertTrue(os.path.isdir(dz_path))
        self.assertTrue(os.path.isfile(dz_file))
        test_dz.delete()
        with self.assertRaises(DeepZoom.DoesNotExist):
            test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertFalse(os.path.isdir(dz_path))
        self.assertFalse(os.path.isfile(dz_file))
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_deepzoom_with_missing_dzi_files(self):
        '''
        4.2) Test attempt to delete DeepZoom with missing deep zoom image files.
        '''
        test_object_name = 'test_dz_4.2'
        test_dz = DeepZoom.objects.get(name=test_object_name)
        dz_path = test_dz.deepzoom_path
        self.assertTrue(os.path.isdir(dz_path))
        if os.path.isdir(dz_path):
            shutil.rmtree(dz_path)
        test_dz.delete()
        with self.assertRaises(DeepZoom.DoesNotExist):
            test_dz = DeepZoom.objects.get(name=test_object_name)
        self.assertFalse(os.path.isdir(dz_path))
        reSet(settings.MEDIA_ROOT)
    
    
    def test_delete_all_deepzooms_using_bulk_delete_action(self):
        '''
        4.3) Test deleting multiple deep zoom images using bulk delete action.
        '''
        test_dzs = DeepZoom.objects.all()
        dz_paths = [test_dz.deepzoom_path for test_dz in test_dzs]
        for dz_path in dz_paths:
            self.assertTrue(os.path.isdir(dz_path))
        for test_dz in test_dzs:
            test_dz.delete()
        for test_dz in test_dzs:
            with self.assertRaises(DeepZoom.DoesNotExist):
                DeepZoom.objects.get(name=test_dz.name)
        for dz_path in dz_paths:
            self.assertFalse(os.path.isdir(dz_path))
        reSet(settings.MEDIA_ROOT)
    
    
    def suite():
        tests = ['delete_deepzoom_by_calling_delete_method_directly', 
                 'delete_deepzoom_with_missing_dzi_files', 
                 'delete_all_deepzooms_using_bulk_delete_action']

        return unittest.TestSuite(map(DeleteDeepZoomTestCase, tests))
#end DeleteDeepZoomTestCase


@override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
                   DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
                   DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
class DeepZoomFirstTemplateTagTestCase(SimpleTestCase):
    '''
    5.) Class tests DeepZoom JavaScript inclusion template tag.
    '''
    def tearDown(self):
        for dz in DeepZoom.objects.all():
            dz.delete()
        reSet(settings.MEDIA_ROOT)
    
    
    def test_call_template_tag_without_deepzoom_object(self):
        '''
        5.1) Test calling deepzoom_js template tag without first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_5.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    
    
    def test_call_template_tag_without__deep_zoom_div_id__argument(self):
        '''
        5.2) Test calling deepzoom_js template tag without second 
            (Deep Zoom div ID) argument.
        '''
        test_object_name = 'test_dz_5.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    
    
    def test_call_template_tag_with_extra_argument(self):
        '''
        5.3) Test calling deepzoom_js template tag with extra argument.
        '''
        test_object_name = 'test_dz_5.3'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        except_string = "The u'deepzoom_js' tag requires two arguments: 'Deep Zoom object' and 'Deep Zoom div ID'."
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj 'deepzoom_div' extra %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    
    
    def test_call_template_tag_with_first_argument_quoted(self):
        '''
        5.4) Test calling deepzoom_js template tag with quoted first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_5.4'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        except_string = "The u'deepzoom_js' tag's 'Deep Zoom object' argument should not be in quotes."
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js 'deepzoom_obj' 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    
    
    def test_call_template_tag_with_unquoted__deep_zoom_div_id__argument(self):
        '''
        5.5) Test calling deepzoom_js template tag with unquoted second 
            (Deep Zoom div ID) argument.
        '''
        test_object_name = 'test_dz_5.5'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        except_string = "The u'deepzoom_js' tag's 'Deep Zoom div ID' argument should be in quotes."
        with self.assertRaisesMessage(TemplateSyntaxError, except_string):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj deepzoom_div %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
    
    
    def suite():
        tests = ['test_call_template_tag_without_deepzoom_object', 
                 'test_call_template_tag_without__deep_zoom_div_id__argument', 
                 'test_call_template_tag_with_extra_argument', 
                 'test_call_template_tag_with_first_argument_quoted', 
                 'test_call_template_tag_with_unquoted__deep_zoom_div_id__argument']

        return unittest.TestSuite(map(DeepZoomFirstTemplateTagTestCase, tests))
#end DeepZoomFirstTemplateTagTestCase


@override_settings(UPLOADEDIMAGE_ROOT = VALID_UPLOADEDIMAGE_ROOT, 
               DEEPZOOM_ROOT = VALID_DEEPZOOM_ROOT, 
               DEEPZOOM_PARAMS = VALID_DEEPZOOM_PARAMS)
class DeepZoomSecondTemplateTagTestCase(TestCase):
    '''
    6.) Class tests DeepZoom JavaScript inclusion template tag.
    '''
    def test_call_template_tag_with_first_argument_unrecognized_object(self):
        '''
        6.1) Test calling deepzoom_js template tag with unrecognized first 
            (Deep Zoom object) argument.
        '''
        test_object_name = 'test_dz_6.1'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        out = Template("{% load deepzoom_tags %}"
                       "{% deepzoom_js unknown_obj 'deepzoom_div' %}"
                       ).render(Context({'deepzoom_obj': test_dz}))
        self.assertEqual(out, "")
    
    
    def test_call_template_tag_with_correct_number_and_format_arguments(self):
        '''
        6.2) Test calling deepzoom_js template tag with correct number and 
            format of arguments.
        '''
        test_object_name = 'test_dz_6.2'
        image_path = os.path.join(settings.TEST_ROOT, TEST_IMAGE_PORTRAIT)
        image = simulate_uploaded_file(image_path)
        test_dz = TestImage.objects.create(uploaded_image=image, 
                                           name=test_object_name, 
                                           create_deepzoom=True)
        with self.assertTemplateUsed('deepzoom/deepzoom_js.html'):
            out = Template("{% load deepzoom_tags %}"
                           "{% deepzoom_js deepzoom_obj 'deepzoom_div' %}"
                           ).render(Context({'deepzoom_obj': test_dz}))
            self.assertNotEqual(out, "")
    
    
    def suite():
        tests = ['test_call_template_tag_with_first_argument_unrecognized_object', 
                 'test_call_template_tag_with_correct_number_and_format_arguments']

        return unittest.TestSuite(map(DeepZoomSecondTemplateTagTestCase, tests))
#end DeepZoomSecondTemplateTagTestCase


#EOF django-deepzoom tests