from datetime import datetime, timezone
import pytz

def getNow ():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

