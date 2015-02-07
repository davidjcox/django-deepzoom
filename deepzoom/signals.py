'''django-deepzoom signals'''

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

try:
    from django.utils.text import slugify
except ImportError:
    try:
        from django.template.defaultfilters import slugify
    except ImportError:
        print("Unable to import `slugify`.")

import six

from .models import UploadedImage, DeepZoom
from .utils import receiver_subclasses, is_django_version_greater_than



DJANGO_SAVE_UPDATEABLE = is_django_version_greater_than(1, 4)


@receiver_subclasses(pre_save, sender=UploadedImage, _dispatch_uid="d__ui_a_dz")
def delete__uploadedimage_and_deepzoom(instance, **kwargs):
    """
    If image already exists, but new image uploaded, delete existing image file.
    If deepzoom image is associated with previous uploaded image, delete it.
    """
    uploaded_field_changed = ('uploaded_image' in instance.changed_fields)
    
    if uploaded_field_changed:
        previous_image = instance.get_field_diff('uploaded_image')[0]
        if previous_image:
            instance.delete_image_file(previous_image.path)
            if (instance.associated_deepzoom is not None):
                instance.associated_deepzoom.delete()


@receiver_subclasses(pre_save, sender=UploadedImage, _dispatch_uid="s__ui")
def slugify__uploadedimage(instance, slugify=slugify, **kwargs):
    """
    Slugifies UploadedImage `name`.
    """
    name_field_changed = ('name' in instance.changed_fields)
    
    if (name_field_changed or not instance.slug):
        instance.slug = slugify(six.u(instance.name))
    

@receiver_subclasses(post_save, sender=UploadedImage, _dispatch_uid="c_u__dz")
def create_update__deepzoom(instance, created, **kwargs):
    """
    Kicks off deepzoom creation sequence by creating a deepzoom instance.
    Associates image to deepzoom with returned deepzoom reference.
    """
    uploaded_field_changed = ('uploaded_image' in instance.changed_fields)
    create_deepzoom_changed = ('create_deepzoom' in instance.changed_fields)
    
    if instance.create_deepzoom:
        if (created or uploaded_field_changed or create_deepzoom_changed):
            dz = instance.create_deepzoom_image()
            instance.associated_deepzoom = dz
            instance.create_deepzoom = False
            if DJANGO_SAVE_UPDATEABLE:
                instance.save(update_fields=['associated_deepzoom', 
                                             'create_deepzoom'])
            else:
                instance.save()


@receiver_subclasses(pre_delete, sender=UploadedImage, _dispatch_uid="d__ui")
def delete__uploadedimage(instance, **kwargs):
    """
    Handles deletion of uploaded image file from storage.
    """
    instance.delete_image_file(instance.uploaded_image.path)
    if (instance.associated_deepzoom is not None):
        instance.associated_deepzoom.delete()


@receiver(pre_save, sender=DeepZoom, dispatch_uid="s__d")
def slugify__deepzoom(instance, slugify=slugify, **kwargs):
    """
    Slugifies Deepzoom `name`.
    """
    name_field_changed = ('name' in instance.changed_fields)
    
    if (name_field_changed or not instance.slug):
        instance.slug = slugify(six.u(instance.name))


@receiver(post_save, sender=DeepZoom, dispatch_uid="c__dz_f")
def create__deepzoom_files(instance, created, **kwargs):
    """
    Processes deepzoom from uploaded image and saves deepzoom files to storage.
    """
    if created:
        _deepzoom_image, _deepzoom_path = instance.create_deepzoom_files()
        instance.deepzoom_image = _deepzoom_image
        instance.deepzoom_path = _deepzoom_path
        if DJANGO_SAVE_UPDATEABLE:
            instance.save(update_fields=['deepzoom_image', 'deepzoom_path'])
        else:
            instance.save()

@receiver(pre_delete, sender=DeepZoom, dispatch_uid="d__d")
def delete__deepzoom(instance, **kwargs):
    """
    Handles deletion of deepzoom image files from storage.
    """
    instance.delete_deepzoom_files()


#EOF - django-deepzoom signals
