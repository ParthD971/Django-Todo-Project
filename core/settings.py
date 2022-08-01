import os
from dotenv import load_dotenv
load_dotenv()

IS_PRODUCTION = os.environ.get('IS_PRODUCTION') == 'TRUE'

if IS_PRODUCTION:
    from .conf.production.settings import *
else:
    from .conf.development.settings import *


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
