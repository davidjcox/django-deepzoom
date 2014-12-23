'''django-deepzoom models'''
from django.db import models
from django.conf import settings
from django.contrib import admin

try:
    from django.utils.text import slugify
except ImportError:
    try:
        from django.template.defaultfilters import slugify
    except ImportError:
        print("Unable to import `slugify`.")
except:
    print("Unable to import `slugify`.")

import os
import sys
import shutil
# import six

from . import deepzoom



#===============================================================================


class DeepZoom(models.Model):
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
    
    
    name = models.CharField(unique=True, 
                            max_length=64)
    
    slug = models.SlugField(max_length=64, 
                            unique=True, 
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
        #Return parameter from settings, filling in default values as needed.
        return dz_params.get(dz_param, self.DEFAULT_DEEPZOOM_PARAMS[dz_param])
    
    
    def save(self, *args, **kwargs):
        #Accommodate unicode differences between Python 2 & 3.
        try:
            self.slug = slugify(unicode(self.name))
        except NameError:
            self.slug = slugify(self.name)
                
        if not (self.deepzoom_image and self.deepzoom_path):
            #Try to load deep zoom parameters, otherwise assign default values.
            try:
                dz_params = settings.DEEPZOOM_PARAMS
            except AttributeError:
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
            
            dz_filename = self.name + '.dzi'
            
            #Try to load deep zoom root, otherwise assign default value.
            try:
                dz_deepzoom_root = settings.DEEPZOOM_ROOT
            except AttributeError:
                dz_deepzoom_root = self.DEFAULT_DEEPZOOM_ROOT
            
            try:
                if not isinstance(dz_deepzoom_root, str):
                    raise AttributeError("`DEEPZOOM_ROOT` must be a string.")
            except NameError:
                try:
                    if not isinstance(dz_deepzoom_root, basestring):
                        raise AttributeError("`DEEPZOOM_ROOT` must be a string.")
                except:
                    raise
            except:
                    raise
            
            # if not isinstance(dz_deepzoom_root, six.string_types):
                # raise AttributeError("`DEEPZOOM_ROOT` must be a string.")
            
            dz_media_root = os.path.join(settings.MEDIA_ROOT, dz_deepzoom_root)
            
            #Create deep zoom media root if defined but not actually exists.
            if not os.path.isdir(dz_media_root):
                try:
                    os.makedirs(dz_media_root)
                except OSError as err:
                    print("OS error({0}): {1}".format(err.errno, err.strerror))
                except IOError as err:
                    print("I/O error({0}): {1}".format(err.errno, err.strerror))
                except:
                    raise
            
            dz_relfilename = os.path.join(dz_deepzoom_root, self.name, dz_filename)
            dz_fullfilepath = os.path.join(dz_media_root, self.name)
            dz_fullfilename = os.path.join(dz_fullfilepath, dz_filename)
            
            #Process deep zoom image and save to file system.
            try:
                creator.create(self.associated_image, dz_fullfilename)
            except OSError as err:
                print("OS error({0}): {1}".format(err.errno, err.strerror))
            except IOError as err:
                print("I/O error({0}): {1}".format(err.errno, err.strerror))
            except:
                print("Unexpected deep zoom creation error:", sys.exc_info())
                raise

            self.deepzoom_image = dz_relfilename # Needed by template.
            self.deepzoom_path = dz_fullfilepath # Needed by `delete` method.
        
        super(DeepZoom, self).save(*args, **kwargs)
    
    
    def delete(self, *args, **kwargs):
        try:
            shutil.rmtree(self.deepzoom_path, ignore_errors=True)
        except:
            pass
        
        super(DeepZoom, self).delete(*args, **kwargs)
    
    
    def __unicode__(self):
        return '%s' % (self.name)
    
    def __str__(self):
        return '%s' % (self.name)
# /DeepZoom


class UploadedImage(models.Model):
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
    
    
    def get_uploaded_image_root(instance, filename):
        try:
            uploaded_image_root = settings.UPLOADEDIMAGE_ROOT
        except AttributeError:
            uploaded_image_root = instance.DEFAULT_UPLOADEDIMAGE_ROOT
        
        try:
            if not isinstance(uploaded_image_root, str):
                raise AttributeError("`UPLOADEDIMAGE_ROOT` must be a string.")
        except NameError:
            try:
                if not isinstance(uploaded_image_root, basestring):
                    raise AttributeError("`UPLOADEDIMAGE_ROOT` must be a string.")
            except:
                raise
        except:
                raise
        
        # if not isinstance(uploaded_image_root, six.string_types):
                # raise AttributeError("`DEEPZOOM_ROOT` must be a string.")
        
        return (os.path.join(uploaded_image_root, filename))
    
    
    uploaded_image = models.ImageField(upload_to=get_uploaded_image_root, 
                                       height_field='height', 
                                       width_field='width')
    
    name = models.CharField(max_length=64, 
                            unique=True, 
                            help_text="64 chars.  Must be unique.")
    
    slug = models.SlugField(max_length=64, 
                            unique=True, 
                            editable=False)
    
    height = models.PositiveIntegerField(editable=False, 
                                         help_text="Auto-filled by PIL.")
    
    width = models.PositiveIntegerField(editable=False, 
                                        help_text="Auto-filled by PIL.")
    
    #Optionally generate deep zoom from image if set to True.
    create_deepzoom = models.BooleanField(default=False, 
                                          help_text="Generate deep zoom?")
    
    deepzoom_already_created = models.BooleanField(default=False, 
                                                   editable=False)
    
    created = models.DateTimeField(auto_now_add=True, 
                                   editable=False)
    
    updated = models.DateTimeField(auto_now=True, 
                                   editable=False)
    
    
    def save(self, *args, **kwargs):
        #Accommodate unicode differences between Python 2 & 3.
        try:
            self.slug = slugify(unicode(self.name))
        except NameError:
            self.slug = slugify(self.name)
                
        if not self.create_deepzoom:
            super(UploadedImage, self).save(*args, **kwargs)
        
        #Create deep zoom tiled image and link this image to it.
        if self.create_deepzoom and not self.deepzoom_already_created:
            self.create_deepzoom = False
            self.deepzoom_already_created = True
            try:
                super(UploadedImage, self).save(*args, **kwargs)
                dz = DeepZoom(associated_image=self.uploaded_image.path, 
                              name=self.name)
                dz.save()
            except (TypeError, ValueError, AttributeError) as err:
                print("Error: Incorrect deep zoom parameter(s) in settings.py: {0}".format(err))
                raise
            except:
                print("Unexpected error creating deep zoom: {0}".format(sys.exc_info()[1:2]))
                raise
                
    
    def delete(self, *args, **kwargs):
        try:
            os.remove(self.uploaded_image.path)
        except OSError:
            pass
        
        super(UploadedImage, self).delete(*args, **kwargs)
    
    
    def __unicode__(self):
        return '%s' % (self.name)
    
    def __str__(self):
        return '%s' % (self.name)
# /UploadedImage


class TestImage(UploadedImage):
    '''
    Test class included solely for testing.  Feel free to delete it or change it
    if you've no need to run the app tests.
    '''
# /TestImage


#EOF - django-deepzoom models
