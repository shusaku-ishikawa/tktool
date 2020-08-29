import os

k = 'django_env'
if k in os.environ and os.environ[k] == 'prod':
   from .prod import *
else:
   from .dev import *
