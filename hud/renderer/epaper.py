import os
from PIL import Image,ImageDraw,ImageFont
from cairosvg import svg2png
import io
import pytz
from ..display import RaspberryPi, EPD

from .graphic import generateGraphic

class DisplayFrame:
    def __init__ (self, width, height):
        self.black_image = Image.new('1', (width, height), 255)
        self.red_image = Image.new('1', (width, height), 255)

    def _applySVG (self, img, svg_str):
        png_bytes = svg2png(svg_str)
        graphic = Image.open(io.BytesIO(png_bytes))
        img.paste(graphic)

    def drawBlack (self, svg_str):
        self._applySVG(self.black_image, svg_str)

    def drawRed (self, svg_str):
        self._applySVG(self.red_image, svg_str)


class Renderer:
    def __init__ (self):
        driver = RaspberryPi()
        self.display = EPD(driver)

    def render (self, data):
        frame = DisplayFrame(self.display.width, self.display.height)
        graphic_b = generateGraphic(data, 'black')
        graphic_r = generateGraphic(data, 'red')
        # with open('./last_black.svg','w') as f:
        #     f.write(graphic_b)
        # with open('./last_red.svg','w') as f:
        #     f.write(graphic_r)
        frame.drawBlack(graphic_b)
        frame.drawRed(graphic_r)
        self._flush(frame)

    def _flush (self, frame):
        self.display.init()
        self.display.show(
            self.display.getbuffer(frame.black_image),
            self.display.getbuffer(frame.red_image)
        )
        self.display.sleep()
