from display import EPD
from epdconfig import RaspberryPi
#from fetch_data import loadOrFetchData
#from renderer import Renderer
from time import sleep

driver = RaspberryPi()
display = EPD(driver)
# renderer = Renderer(display)

from cairosvg import svg2png
import io
from PIL import Image

print('initialized')

img_bytes = svg2png(url='./test.svg')

print(len(img_bytes), 'bytes')

width = 800
height = 480
print(width, height)
graphic = Image.open(io.BytesIO(img_bytes))
print(graphic)

img_b = Image.new('1', (width, height), 255)
img_r = Image.new('1', (width, height), 255)

print(img_b, img_r)

print('compositing')
img_b.paste(graphic)

print('connecting')
display.init()
print('displaying')
display.show(display.getbuffer(img_b), display.getbuffer(img_r))
print('disconnecting')
display.sleep()
print('done')
# while True:
#     data = loadOrFetchData
#     renderer.render(data)
#     sleep(60)

