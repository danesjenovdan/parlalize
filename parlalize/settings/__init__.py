import os

DJANGO_SETTINGS_MODULE = os.getenv('DJANGO_SETTINGS_MODULE', False)
if not DJANGO_SETTINGS_MODULE:
	print('You need to set the DJANGO_SETTINGS_MODULE environment variable.')
