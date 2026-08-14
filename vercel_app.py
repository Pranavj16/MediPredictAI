import sys
import os

# Add django_app directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_app'))

from django_app.config.wsgi import application

# Vercel requires a variable named 'app' exposing the WSGI interface
app = application
