'''django-deepzoom models'''
from django.db import models
from django.conf import settings
from django.contrib import admin

import os
import sys
import codecs
from string import punctuation as punctuation_marks
import shutil

from . import deepzoom


#===============================================================================


def slugify(string_to_convert=None):
    '''
    Custom slug generator.
    
    Converts common separators ('-', '_', '.') into spaces, reduces consecutive 
    
    spaces to single spaces, deletes non-URL-compliant punctuation, lowercases,  
    
    strips leading spaces, and finally converts spaces into dashes.
    
    E.g. " Hey!  What is this.py? " --> "hey-what-is-this-py"
    '''
    preserve_charmap = str.maketrans({'-': ' ', '_': ' ', '.': ' '})
    
    invalid_charmap = str.maketrans(dict(zip(punctuation_marks, [None] * 32)))
    
    substituted_string = string_to_convert.translate(preserve_charmap)
    
    reduced_string = ' '.join(substituted_string.split())
    
    translated_string = reduced_string.translate(invalid_charmap)
    
    converted_string = translated_string.strip().lower().replace(' ', '-')
    
    return(converted_string)
#end slugify 


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
        verbose_name = "Deep Zoom Image"
        verbose_name_plural = "Deep Zoom Images"
        get_latest_by = "created"
    
    
    DEFAULT_DEEPZOOM_ROOT = 'deepzoom_images'
    DEFAULT_DEEPZOOM_PARAMS = [256, 1, "jpg", 0.85, "antialias"]
    
    
    name = models.CharField("Name", 
                            unique=True, 
                            max_length=64)
    
    slug = models.SlugField(max_length=64, 
                            unique=True, 
                            editable=False)
    
    associated_image = models.CharField("Associated Image Path", 
                                        max_length=256, 
                                        editable=False)
    
    deepzoom_image = models.CharField("Deep Zoom Image", 
                                      max_length=256, 
                                      editable=False)
    
    deepzoom_path = models.CharField("Deep Zoom File", 
                                     max_length=256, 
                                     editable=False)
    
    deepzoom_xml = models.CharField("Deep Zoom XML", 
                                    max_length=256, 
                                    editable=False)
    
    created = models.DateTimeField("Created", 
                                   auto_now_add=True, 
                                   editable=False)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = self.slug
        
        if not (self.deepzoom_image and self.deepzoom_xml):
            #Try to load deep zoom parameters, otherwise assign default values.
            try:
                (tile_size, 
                 tile_overlap, 
                 tile_format, 
                 image_quality, 
                 resize_filter) = settings.DEEPZOOM_PARAMS
            except:
                (tile_size, 
                 tile_overlap, 
                 tile_format, 
                 image_quality, 
                 resize_filter) = self.DEFAULT_DEEPZOOM_PARAMS
            
            #Initialize deep zoom creator.
            creator = deepzoom.ImageCreator(tile_size, 
                                            tile_overlap, 
                                            tile_format, 
                                            image_quality, 
                                            resize_filter)
            
            dz_filename = self.name + '.dzi'
            
            #Try to load deep zoom root, otherwise assign default value.
            try:
                dz_deepzoom_root = settings.DEEPZOOM_ROOT
            except:
                dz_deepzoom_root = self.DEFAULT_DEEPZOOM_ROOT
            
            dz_mediaroot = os.path.join(settings.MEDIA_ROOT, dz_deepzoom_root)
            
            #Create deep zoom media root if defined but not physically created.
            if not os.path.isdir(dz_mediaroot):
                try:
                    os.makedirs(dz_mediaroot)
                except OSError as err:
                    print("OS error({0}): {1}".format(err.errno, err.strerror))
                except IOError as err:
                    print("I/O error({0}): {1}".format(err.errno, err.strerror))
                except:
                    raise
            
            dz_relfilepath = os.path.join(dz_deepzoom_root, self.name)
            dz_relfilename = os.path.join(dz_relfilepath, dz_filename)
            dz_fullfilepath = os.path.join(settings.MEDIA_ROOT, dz_relfilepath)
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

            self.deepzoom_image = dz_relfilename
            self.deepzoom_path = dz_fullfilepath
            
            #Read generated XML metadata and save to deepzoom_xml for template use.
            try:
                with codecs.open(dz_fullfilename, "r", "utf-8-sig") as dz_file:
                    self.deepzoom_xml = dz_file.read()
            except IOError as err:
                print("I/O error({0}): {1}".format(err.errno, err.strerror))
        
        super(DeepZoom, self).save(*args, **kwargs)
    
    
    def delete(self, *args, **kwargs):
        try:
            shutil.rmtree(self.deepzoom_path, ignore_errors=True)
        except:
            pass
        
        super(DeepZoom, self).delete(*args, **kwargs)
    
    
    def __unicode__(self):
        return '%s' % (self.name)
#end DeepZoom


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
        except:
            uploaded_image_root = instance.DEFAULT_UPLOADEDIMAGE_ROOT
        
        return (os.path.join(uploaded_image_root, filename))
    
    
    uploaded_image = models.ImageField(upload_to=get_uploaded_image_root, 
                                       height_field='height', 
                                       width_field='width')
    
    name = models.CharField("Image Name", 
                            max_length=64, 
                            unique=True, 
                            help_text="64 chars.  Must be unique.")
    
    slug = models.SlugField(max_length=64, 
                            unique=True, 
                            editable=False)
    
    height = models.PositiveIntegerField("Image Height", 
                                         editable=False, 
                                         help_text="Auto-filled by PIL.")
    
    width = models.PositiveIntegerField("Image Width", 
                                        editable=False, 
                                        help_text="Auto-filled by PIL.")
    
    #Optionally generate deep zoom from image if set to True.
    create_deepzoom = models.BooleanField(default=False, 
                                          help_text="Generate deep zoom?")
    
    deepzoom_already_created = models.BooleanField(default=False, 
                                                   editable=False)
    
    #Link this image to generated deep zoom.
    # associated_deepzoom = models.ForeignKey(DeepZoom, 
                                            # related_name='%(app_label)s_%(class)s_related', 
                                            # null=True, 
                                            # editable=False, 
                                            # on_delete=models.SET_NULL)
    
    created = models.DateTimeField("Created", 
                                   auto_now_add=True, 
                                   editable=False)
    
    updated = models.DateTimeField("Updated", 
                                   auto_now=True, 
                                   editable=False)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = self.slug
        
        if (not self.create_deepzoom):
            super(UploadedImage, self).save(*args, **kwargs)
        
        #Create deep zoom tiled image and link this image to it.
        if self.create_deepzoom and not self.deepzoom_already_created:
            try:
                self.create_deepzoom = False
                self.deepzoom_already_created = True
                super(UploadedImage, self).save(*args, **kwargs)
                dz = DeepZoom(associated_image=self.uploaded_image.path, 
                              name=self.name)
                dz.save()
                #self.associated_deepzoom = dz
            except (TypeError, ValueError):
                # self.associated_deepzoom = None
                self.deepzoom_already_created = False
                print("Error: Incorrect deep zoom parameter(s) in settings.py.")
            except:
                # self.associated_deepzoom = None
                self.deepzoom_already_created = False
                print("Unexpected error creating deep zoom:{0}".format(sys.exc_info()[1:2]))
                raise
                
    
    def delete(self, *args, **kwargs):
        try:
            os.remove(self.uploaded_image.path)
        except OSError:
            pass
        
        super(UploadedImage, self).delete(*args, **kwargs)
    
    
    def __unicode__(self):
        return '%s' % (self.name)
#end UploadedImage


class TestImage(UploadedImage):
    '''
    Test class included solely for testing.  Feel free to delete it or change it
    if you've no need to run the app tests.
    '''
#end TestImage


#EOF django-deepzoom models
