"""
WSGI config for tmp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/bitnami/projects/iplan')
os.environ['PYTHON_EGG_CACHE'] = '/opt/bitnami/projects/iplan/egg_cache'

os.environ['DJANGO_SETTINGS_MODULE'] = 'iplan.settings'

application = get_wsgi_application()
