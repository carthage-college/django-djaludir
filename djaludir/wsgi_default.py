import os
import time
import traceback
import signal
import sys

sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
#sys.path.append('/data2/django_trunk/')
#sys.path.append('/data2/django_1.5.5/')
#sys.path.append('/data2/django_1.6/')
#sys.path.append('/data2/django_1.8/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/django-djaludir/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
# Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'djaludir.settings'
os.environ['PYTHON_EGG_CACHE'] = '/var/cache/python/.python-eggs'
os.environ['TZ'] = 'America/Chicago'
# informix
os.environ['INFORMIXSERVER'] = ''
os.environ['DBSERVERNAME'] = ''
os.environ['INFORMIXDIR'] = ''
os.environ['ODBCINI'] = ''
os.environ['ONCONFIG'] = ''
os.environ['INFORMIXSQLHOSTS'] = ''
os.environ['LD_LIBRARY_PATH'] = '$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:/usr/lib/apache2/modules:$INFORMIXDIR/lib/cli'
os.environ['LD_RUN_PATH'] = ''
# wsgi
from django.core.wsgi import get_wsgi_application

# for production:
# uncomment out the following and comment out the try/except below
#application = get_wsgi_application()

try:
    application = get_wsgi_application()
except Exception:
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
    exit(-1)
