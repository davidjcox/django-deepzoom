===============
django-deepzoom
===============

Django-deepzoom is a drop-in Django app for the creation and use of Deep Zoom 
tiled images.  It handily integrates Daniel Gasienica's and Kapil Thangavelu's 
deepzoom.py image generator and the OpenSeadragon deep zoom viewer into a set 
of model classes and template tags which programmatically generate tiled images 
and all JavaScript necessary for their instantiation into templates.

Detailed documentation is available on http://django-deepzoom.readthedocs.org/en/latest/.

:Author:    David J Cox

:Contact:   <davidjcox.at@gmail.com>

:Version:   3.0

Let me know what you think of it...

What's New?
-----------

Django-deepzoom 3.0 involves major architectural changes so a major version bump is necessary. It introduces signal-based save, a new `DEFAULT_CREATE_DEEPZOOM_OPTION` setting, better file management, and decoupled file locations. It continues to be Python 2/3 compatible, Django 1.4+ compatible, and Pillow 1.7.8+ compatible.

Signal-based save: Save/update code has been completely removed from model save/delete methods and distributed amongst signal handler methods.  This was done to improve inter-model coordination and to beter manage state transitions during field updates.  Fields that could not be updated before, e.g. `UploadedImage.uploaded_image` now are handled in the expected way.  If an entirely new image is uploaded to an existing `UploadedImage` subclass and is saved, the previous `uploaded_image` will be deleted, the previous associated deepzoom will be deleted, the new uploaded image saved to disk, and an entirely new deepzoom will be generated from the new image.

New `DEFAULT_CREATE_DEEPZOOM_OPTION` setting: The default value of the `create_deepzoom` field can be controlled globally by setting the `DEFAULT_CREATE_DEEPZOOM_OPTION` to `True` or `False`.  New instances of a `UploadedImage` subclass will be set to always create a deepzoom or never to create a deepzoom.

Better file management: Instead of relying on the default Django file management policy of 'never delete/always save', instance saves, updates, and deletes now involve corresponding file behavior to keep the file system free from overflowing.

Decoupled file locations: File locations saved to instances are now computed and saved relative to `MEDIA_ROOT` instead of being absolute file paths.

Run tests
---------
After django-deepzoom has been installed, you may want to sanity check it by 
running tests, like this:

    python manage.py test deepzoom --settings=deepzoom.test.test_settings

    ATTENTION:
        Some of the negative tests are intended to throw exceptions.  The error 
        text will display mixed in with the test results.  THAT IS EXPECTED!

        If the end result is **OK** then all tests have passed.  Enjoy.


Quick start
-----------

1.) Install "django-deepzoom" like this:

    pip install -U django-deepzoom


or, like this:

    wget https://pypi.python.org/packages/source/d/django-deepzoom/django-deepzoom-3.0.tar.gz
    tar -xvf django-deepzoom-3.0.tar.gz
    cd django-deepzoom-3.0
    python setup.py install

2.) Add "deepzoom" to your INSTALLED_APPS setting.  Django 1.7 introduced the 
`AppConfig.ready()` entry point for app intialization which is needed for 
the new signals design (in that version of Django).  That means the 
django-deepzoom app needs to be specified one way in Django 1.7+ and the 
traditional way in previous Django versions.
In Django 1.7+ add the app like this::

    (in settings.py)
    
    INSTALLED_APPS = (
        ...
        'deepzoom.apps.DeepZoomAppConfig',
        ...
    )

However, in Django 1.6 and before, add the app the traditional way, like this::

    (in settings.py)
    
    INSTALLED_APPS = (
        ...
        'deepzoom',
        ...
    )

3.) Sub-class the '`UploadedImage`' model class as your own (image-based) class, 
something like this:

    (in models.py)
    
    from deepzoom.models import DeepZoom, UploadedImage
      
    class MyImage(UploadedImage):
        '''
        Overrides UploadedImage base class.
        '''
        pass

4.) Import signals.py. If using Django 1.6 or before, the signals module must 
be imported after the model definitions have been parsed.  This means the 
signals.py import statement must either be added to the end of the models.py 
file or in the app __init__.py file.  The former avoids breaking test 
coverage, so may be preferable. 
Import the signals.py file, like this::

    (in models.py)
    
    ...
    model definitions...
    ...
    
    import deepzoom.signals

5.) Run `python manage.py syncdb` to create the django-deepzoom models.

6.) Add an appropriate URL to your Urlconf, something like this::

    (in urls.py)
    
    from deepzoom.views import deepzoom_view
    
    urlpatterns = patterns('', 
        ...
        url(r'^deepzoom/(?P<passed_slug>\b[a-z0-9\-]+\b)', 
            deepzoom_view, 
            name="v_deepzoom"), 
        ...
    )

7.) Write a view that queries for a specific DeepZoom object and passes it to a 
template, something like this:
   
    (in views.py)
    
    from deepzoom.models import DeepZoom
      
    def deepzoom_view(request, passed_slug=None):
      try:
          _deepzoom_obj = DeepZoom.objects.get(slug=passed_slug)
      except DeepZoom.DoesNotExist:
          raise Http404
      return render_to_response('deepzoom.html', 
                                {'deepzoom_obj': _deepzoom_obj}, 
                                context_instance=RequestContext(request))

8.) In your template, create an empty div with a unique ID.  Load the deepzoom 
tags and pass the deepzoom object and deepzoom div ID to the template tag 
inside a <script> block in the body like this:

    (in e.g. deepzoom.html)
    
    {% extends "base.html" %}
      
    {% load deepzoom_tags %}
      
    <div id="deepzoom_div"></div>
    
    <script>{% deepzoom_js deepzoom_obj "deepzoom_div" %}</script>

9.) Run `python manage.py collectstatic` to collect your static files into STATIC_ROOT.

10.) Start the development server and visit `http://127.0.0.1:8000/admin/` to 
upload an image to the associated model (you'll need the Admin app enabled).
Be sure to check the `Generate deep zoom?` checkbox for that image before 
saving it.

11.) Navigate to the page containing the deep zoom image and either click/touch 
it or click/touch the overlaid controls to zoom into and out of the tiled 
image.

`**Behold!** <http://django-deepzoom.invocatum.net/featured/>`_

.