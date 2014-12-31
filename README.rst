===============
django-deepzoom
===============

Django-deepzoom is a drop-in Django app for the creation and use of Deep Zoom 
tiled images.  It handily integrates Daniel Gasienica's and Kapil Thangavelu's 
deepzoom.py image generator and the OpenSeadragon deep zoom viewer into a set 
of model classes and template tags which programmatically generate tiled images 
and all JavaScript necessary for their instantiation into templates.

Detailed documentation is available on 
`ReadTheDocs <http://django-deepzoom.readthedocs.org/en/latest/>`_.

:Author:    David J Cox

:Contact:   <davidjcox.at@gmail.com>

:Version:   2.0

Let me know what you think of it...

What's New?
-----------

Django-deepzoom 2.0 is a new unified version!  It's now compatible with both Python 2 and Python 3, all versions of Django from 1.4 onward, and with Pillow 1.7.8 onward.  Now it's truly drop-in ready...
The OpenSeadragon open source deep zoom viewer has replaced the Microsoft Seadragon control.  The project benefits from a truly open solution free from dependencies.
The deepzoom generator parameters have been changed from a arg list to a kwarg dictionary to make things easier.  More robust input checking and better exception handling have also been added.

Run tests
---------
After django-deepzoom has been installed, you may want to sanity check it by running tests, like this::

    python manage.py test deepzoom --settings=deepzoom.test.test_settings

.. attention::
        Some of the negative tests are intended to throw exceptions.  The error text will display mixed in with the test results.  THAT IS EXPECTED!

        If the end result is **OK** then all tests have passed.  Enjoy.


Quick start
-----------

1.) Install "django-deepzoom" like this::

    pip install -U django-deepzoom


or, like this::

    wget https://pypi.python.org/packages/source/d/django-deepzoom/django-deepzoom-2.0.tar.gz
    tar -xvf django-deepzoom-2.0.tar.gz
    cd django-deepzoom-2.0
    python setup.py install

2.) Add "deepzoom" to your INSTALLED_APPS setting like this::

    (in settings.py)
      
    INSTALLED_APPS = (
        ...
        'deepzoom',
        ...
    )

3.) Sub-class the '`UploadedImage`' model class as your own (image-based) class, something like this::

    (in models.py)
      
    from deepzoom.models import DeepZoom, UploadedImage
	from django.contrib import admin
      
    class MyImage(UploadedImage):
		'''
		Overrides UploadedImage base class.
		'''
		pass
	
	admin.site.register(MyImage)

4.) Run `python manage.py syncdb` to create the django-deepzoom models.

5.) Add an appropriate URL to your Urlconf, something like this::

    (in urls.py)
    
    from deepzoom.views import deepzoom_view
    
    urlpatterns = patterns('', 
        ...
        url(r'^deepzoom/(?P<passed_slug>\b[a-z0-9\-]+\b)', 
            deepzoom_view, 
            name="v_deepzoom"), 
        ...
    )

6.) Write a view that queries for a specific DeepZoom object and passes it to a template, something like this::
   
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

7.) In your template, create an empty div with a unique ID.  Load the deepzoom tags and pass the deepzoom object and deepzoom div ID to the template tag in the body like this::

    (in e.g. deepzoom.html)
      
    {% extends "base.html" %}
      
    {% load deepzoom_tags %}
      
    <div id="deepzoom_div" style="width: 1024px; height: 768px;"></div>
    
    {% deepzoom_js deepzoom_obj "deepzoom_div" %}

.. note::
		The deepzoom div should be assigned absolute dimensions.

8.) Run `python manage.py collectstatic` to collect your static files into STATIC_ROOT, specifically so that the OpenSeaDragon files are available.

9.) Start the development server and visit `http://127.0.0.1:8000/admin/` to upload an image to the associated model (you'll need the Admin app enabled).  Be sure to check the `Generate deep zoom?` checkbox for that image before saving it.

10.) Navigate to the page containing the deep zoom image and either click/touch it or click/touch the overlaid controls to zoom into and out of the tiled image.

**Behold!** `A deeply zoomable image! <http://django-deepzoom.invocatum.net/featured/>`_

.