'''django-deepzoom models'''

from django.db import models
from django.conf import settings
from django.contrib import admin

import os
import sys
import shutil
import logging

import six

from .mixins import ModelDiffMixin
from . import deepzoom



logger = logging.getLogger("deepzoom.models")


class DeepZoom(ModelDiffMixin, models.Model):
    '''
    Generates a deep zoom tiled image of an uploaded image.
    
    Creates hierarchy of files and folders in DEEPZOOM_ROOT on save().
    
    Deletes hierarchy of files and folders in DEEPZOOM_ROOT on delete().
    
    REQUIRES: 
        The file path to a uploaded image.
    
    OPTIONAL:
        A DEEPZOOM_ROOT directory is defined in settings.
        
        The DEEPZOOM_PARAMS parameters are defined in settings.
    '''
    class Meta:
        verbose_name = "deep zoom image"
        verbose_name_plural = "deep zoom images"
        ordering = ['name']
        get_latest_by = "created"
    
    
    DEFAULT_DEEPZOOM_ROOT = 'deepzoom_images'
    DEFAULT_DEEPZOOM_PARAMS = {'tile_size': 256,
                               'tile_overlap': 1,
                               'tile_format': "jpg",
                               'image_quality': 0.85,
                               'resize_filter': "antialias"}
    
    
    name = models.CharField(max_length=128,
                            editable=False)
    
    slug = models.SlugField(max_length=128,
                            editable=False)
    
    associated_image = models.CharField(max_length=256,
                                        editable=False)
    
    deepzoom_image = models.CharField(max_length=256,
                                      editable=False)
    
    deepzoom_path = models.CharField(max_length=256,
                                     editable=False)
    
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False)
    
    updated = models.DateTimeField(auto_now_add=True,
                                   editable=False)
    
    
    def get_dz_param(self, dz_param, dz_params):
        """
        Returns parameter from settings, if found.
        Substitutes in default value, if missing.
        """
        return dz_params.get(dz_param, self.DEFAULT_DEEPZOOM_PARAMS[dz_param])
    
    
    def create_deepzoom_files(self):
        """
        Creates deepzoom image from associated uploaded image.
        Attempts to load `DEEPZOOM_PARAMS` and `DEEPZOOM_ROOT` from settings.
        Substitutues default settings for any missing settings.
        """
        
        #Try to load deep zoom parameters, otherwise assign default values.
        try:
            dz_params = settings.DEEPZOOM_PARAMS
        except AttributeError:
            logger.exception("`DEEPZOOM_PARAMS` incorrectly defined!")
            dz_params = self.DEFAULT_DEEPZOOM_PARAMS
        
        if not isinstance(dz_params, dict):
            raise AttributeError("`DEEPZOOM_PARAMS` must be a dictionary.")
        
        _tile_size = self.get_dz_param('tile_size', dz_params)
        _tile_overlap = self.get_dz_param('tile_size', dz_params)
        _tile_format = self.get_dz_param('tile_size', dz_params)
        _image_quality = self.get_dz_param('tile_size', dz_params)
        _resize_filter = self.get_dz_param('tile_size', dz_params)
        
        #Initialize deep zoom creator.
        creator = deepzoom.ImageCreator(tile_size=_tile_size, 
                                        tile_overlap=_tile_overlap, 
                                        tile_format=_tile_format, 
                                        image_quality=_image_quality, 
                                        resize_filter=_resize_filter)
        
        #Try to load deep zoom root, otherwise assign default value.
        try:
            dz_deepzoom_root = settings.DEEPZOOM_ROOT
        except AttributeError:
            dz_deepzoom_root = self.DEFAULT_DEEPZOOM_ROOT
        
        if not isinstance(dz_deepzoom_root, six.string_types):
            raise AttributeError("`DEEPZOOM_ROOT` must be a string.")
        
        media_root = settings.MEDIA_ROOT
        dz_media_root = os.path.join(media_root, dz_deepzoom_root)
        
        #Create deep zoom media root if defined but not actually exists.
        if not os.path.isdir(dz_media_root):
            try:
                os.makedirs(dz_media_root)
            except OSError as err:
                print("OS error({0}): {1}".format(err.errno, err.strerror))
            except IOError as err:
                print("I/O error({0}): {1}".format(err.errno, err.strerror))
            except:
                logger.exception("`DEEPZOOM_ROOT` directory creation failed!")
                raise
        
        dz_filename = self.slug + ".dzi"
        dz_relative_filepath = os.path.join(dz_deepzoom_root, self.slug)
        dz_relative_filename = os.path.join(dz_relative_filepath, dz_filename)
        dz_absolute_filename = os.path.join(media_root, dz_relative_filename)
        dz_associated_image = os.path.join(media_root, self.associated_image)
        
        #Process deep zoom image and save to file system.
        try:
            creator.create(dz_associated_image, dz_absolute_filename)
        except OSError as err:
            print("OS error({0}): {1}".format(err.errno, err.strerror))
        except IOError as err:
            print("I/O error({0}): {1}".format(err.errno, err.strerror))
        except:
            print("Unexpected deep zoom creation error:", sys.exc_info())
            raise
        
        return(dz_relative_filename, dz_relative_filepath)
    
    
    def delete_deepzoom_files(self):
        """
        Deletes file tree for an entire deepzoom image from storage.
        Ignores any errors from operation.
        """
        _deepzooom_path = os.path.join(settings.MEDIA_ROOT, self.deepzoom_path)
        try:
            shutil.rmtree(_deepzooom_path, ignore_errors=True)
        except:
            logger.exception("Deepzoom files deletion failed!")
    
    
    def __unicode__(self):
        return six.u('%s') % (self.name)
    
    def __str__(self):
        return '%s' % (self.name)
# /DeepZoom


class UploadedImage(ModelDiffMixin, models.Model):
    '''
    Abstract class for uploaded images to support creation of DeepZoom images.
    
    Optionally generates a deep zoom image and links it back to this image.
    
    REQUIRED:
        This class must be subclassed in project models.
        
    OPTIONAL:
        A UPLOADEDIMAGE_ROOT directory is defined in settings.
    '''
    class Meta:
        abstract = True
        ordering = ['name']
        get_latest_by = "created"
    
    
    DEFAULT_UPLOADEDIMAGE_ROOT = 'uploaded_images'
    
    try:
        DEFAULT_CREATE_DEEPZOOM = settings.DEFAULT_CREATE_DEEPZOOM_OPTION
    except AttributeError:
        DEFAULT_CREATE_DEEPZOOM = False
    
    if not isinstance(DEFAULT_CREATE_DEEPZOOM, bool):
        raise AttributeError("`DEFAULT_CREATE_DEEPZOOM_OPTION` must be a Boolean.")
    
    
    def get_uploaded_image_root(instance, filename):
        try:
            uploaded_image_root = settings.UPLOADEDIMAGE_ROOT
        except AttributeError:
            uploaded_image_root = instance.DEFAULT_UPLOADEDIMAGE_ROOT
        
        if not isinstance(uploaded_image_root, six.string_types):
                raise AttributeError("`UPLOADEDIMAGE_ROOT` must be a string.")
        
        extension = os.path.splitext(filename)[1]
        filename = instance.slug + extension
        return (os.path.join(uploaded_image_root, filename))
    
    
    uploaded_image = models.ImageField(upload_to=get_uploaded_image_root, 
                                       height_field='height', 
                                       width_field='width')
    
    name = models.CharField(max_length=128,
                            unique=True,
                            help_text="Max 128 characters.")
    
    slug = models.SlugField(max_length=128,
                            editable=False,
                            help_text="(system-constructed)")
    
    height = models.PositiveIntegerField(editable=False,
                                         help_text="(system-calculated)")
    
    width = models.PositiveIntegerField(editable=False,
                                        help_text="(system-calculated)")
    
    #Optionally generate deep zoom from uploaded image if set to True.
    create_deepzoom = models.BooleanField(default=DEFAULT_CREATE_DEEPZOOM,
                                          help_text="Generate deep zoom?")
    
    #Link this image to generated deep zoom.
    associated_deepzoom = models.OneToOneField(DeepZoom,
                                               null=True,
                                               blank=True,
                                               related_name="%(app_label)s_%(class)s",
                                               editable=False,
                                               on_delete=models.SET_NULL)
    
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False)
    
    updated = models.DateTimeField(auto_now=True,
                                   editable=False)
    
    
    def create_deepzoom_image(self):
        """
        Creates and processes deep zoom image files to storage.
        Returns instance of newly created DeepZoom instance for associating   
        uploaded image to it.
        """
        try:
            dz = DeepZoom.objects.create(associated_image=self.uploaded_image.name, 
                                         name=self.name)
        except (TypeError, ValueError, AttributeError) as err:
            print("Error: Incorrect deep zoom parameter(s) in settings.py: {0}".format(err))
            raise
        except:
            print("Unexpected error creating deep zoom: {0}".format(sys.exc_info()[1:2]))
            raise
        return dz
    
    
    def delete_image_file(self, path_of_image_to_delete=None):
        """
        Deletes uploaded image file from storage.
        """
        try:
            os.remove(path_of_image_to_delete)
        except OSError:
            logger.exception("Image file deletion failed!")
    
        
    def __unicode__(self):
        return six.u('%s') % (self.name)
    
    
    def __str__(self):
        return '%s' % (self.name)
# /UploadedImage


#EOF - django-deepzoom models
