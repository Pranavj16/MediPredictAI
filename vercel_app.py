import sys
import os
import django

# Add django_app directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_app'))

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
django.setup()

# Run migrations on startup (necessary for /tmp/db.sqlite3 on Vercel cold start)
from django.core.management import call_command
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Error running migrations on startup: {e}")

from django_app.config.wsgi import application

# Vercel requires a variable named 'app' exposing the WSGI interface
app = application
