from display import EPD
from epdconfig import RaspberryPi
from fetch_data import loadOrFetchData
from renderer import Renderer
from time import sleep
from cairosvg import svg2png
import io
from PIL import Image
from datetime import datetime, timezone, timedelta
import json
import pytz

driver = RaspberryPi()
display = EPD(driver)
renderer = Renderer(display)


# data = None
# with open('./sample-data.json') as f:
#     data = json.load(f)['data']
print('initialized')

while True:
    data = loadOrFetchData(max_age_min=5)
    data['now'] = datetime.utcnow().replace(
        tzinfo=timezone.utc
    ).astimezone(
        tz=pytz.timezone('America/New_York')
    )
    print(data['now'])
    renderer.render(data)
    print('sleeping...')
    sleep(60)
