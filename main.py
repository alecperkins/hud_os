import sys
import os
picdir = '/home/pi/epaper-libs/e-Paper/RaspberryPi_JetsonNano/python/pic'
libdir = '/home/pi/epaper-libs/e-Paper/RaspberryPi_JetsonNano/python/lib'
if os.path.exists(libdir):
    sys.path.append(libdir)

from PIL import Image,ImageDraw,ImageFont

from .epdconfig import RaspberryPi
from .display import EPD


display = EPD(RaspberryPi())

Bimage = Image.new('1', (display.width, display.height), 255)  # 255: clear the frame
Rimage = Image.new('1', (display.width, display.height), 255)
draw_black = ImageDraw.Draw(Bimage)
draw_red = ImageDraw.Draw(Rimage)


font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
draw_black.text((10, 0), 'Hello, world!', font = font24, fill = 0)
draw_red.text((10, 30), 'Hello, world?', font = font24, fill = 0)


display.init()
display.display(epd.getbuffer(Bimage), epd.getbuffer(Rimage))
display.sleep()






import sys
import os
picdir = '/home/pi/epaper-libs/e-Paper/RaspberryPi_JetsonNano/python/pic'
libdir = '/home/pi/epaper-libs/e-Paper/RaspberryPi_JetsonNano/python/lib'
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_V2
# from waveshare_epd import epd7in5
import time
from PIL import Image,ImageDraw,ImageFont
import traceback


epd = epd7in5b_V2.EPD()
# epd = epd7in5bc.EPD()
epd.init()
epd.Clear()
epd.sleep()

Bimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
Rimage = Image.new('1', (epd.width, epd.height), 255)
draw_black = ImageDraw.Draw(Bimage)
draw_red = ImageDraw.Draw(Rimage)


font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
draw_black.text((10, 0), 'Hello, world!', font = font24, fill = 0)
draw_red.text((10, 30), 'Hello, world?', font = font24, fill = 0)

epd.init();epd.display(epd.getbuffer(Bimage), epd.getbuffer(Rimage));epd.sleep()