import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

WEATHERKIT_TOKEN        = os.environ.get('WEATHERKIT_TOKEN')
DARKSKY_API_KEY         = os.environ.get('DARKSKY_API_KEY')
DISPLAY_TZ              = os.environ.get('DISPLAY_TZ', 'UTC')
LATITUDE                = os.environ.get('LATITUDE', 0)
LONGITUDE               = os.environ.get('LONGITUDE', 0)
MTA_REALTIME_API_KEY    = os.environ.get('MTA_REALTIME_API_KEY')

DEBUG_GRAPHIC           = os.environ.get('DEBUG_GRAPHIC') == 'true'