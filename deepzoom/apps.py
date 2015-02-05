"""deepzoom apps"""

from django.apps import AppConfig



class DeepZoomAppConfig(AppConfig):

	name = 'deepzoom'
	verbose_name = 'DeepZoom'

	def ready(self):
		#import signals
		import deepzoom.signals
		