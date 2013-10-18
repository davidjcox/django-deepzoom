===============
django-deepzoom
===============

Django-deepzoom is a drop-in Django app for the creation and use of Deep Zoom 
tiled images.  It handily integrates Daniel Gasienica's and Kapil Thangavelu's 
deepzoom.py image generator, Microsoft's SeaDragon deep zoom viewer, and 
Sean Rice's JavaScript touch events into a set of model classes and template 
tags which programmatically generate tiled images and all JavaScript necessary 
for their instantiation into templates.

Detailed documentation is available on 
`ReadTheDocs <http://django-deepzoom.readthedocs.org/en/latest/>`_.

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

    wget https://pypi.python.org/packages/source/d/django-deepzoom/django-deepzoom-0.2.tar.gz
    tar -xvf django-deepzoom-0.2.tar.gz
    cd django-deepzoom-0.2
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
      
    class MyImage(UploadedImage):
      '''
      Overrides UploadedImage base class.
      '''
      pass

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

7.) In your template, create an empty div with a unique ID.  Load the deepzoom tags and pass the deepzoom object and deepzoom div ID to the template tag inside a <script> block in the body like this::

    (in e.g. deepzoom.html)
      
    {% extends "base.html" %}
      
    {% load deepzoom_tags %}
      
    <div id="deepzoom_div"></div>
    
    <script src="{{ STATIC_URL }}js/vendor/seadragon-min.js"></script>
    
    <script>{% deepzoom_js deepzoom_obj "deepzoom_div" %}</script>

8.) Run `python manage.py collectstatic` to collect your static files into STATIC_ROOT.

9.) Start the development server and visit `http://127.0.0.1:8000/admin/` to upload an image to the associated model (you'll need the Admin app enabled).  Be sure to check the `Generate deep zoom?` checkbox for that image before saving it.

10.) Navigate to the page containing the deep zoom image and either click/touch it or click/touch the overlaid controls to zoom into and out of the tiled image::

    **Behold!**

.