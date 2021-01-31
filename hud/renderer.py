import os
from PIL import Image,ImageDraw,ImageFont

font24 = ImageFont.truetype(
    os.path.join(
        os.path.dirname(__file__),
        'Font.ttc'
    ),
    24
)


class DisplayFrame:
    def __init__ (self, width, height):
        self.black_image = Image.new('1', (width, height), 255)
        self.red_image = Image.new('1', (width, height), 255)
        self.draw_black = ImageDraw.Draw(self.black_image)
        self.draw_red = ImageDraw.Draw(self.red_image)


class Renderer:
    def __init__ (self, display):
        self.display = display

    def render (self, data):
        frame = DisplayFrame(self.display.width, self.display.height)
        renderToFrame(frame, data)
        self.flush(frame)

    def flush (self, frame):
        self.display.init()
        self.display.show(
            self.display.getbuffer(frame.black_image),
            self.display.getbuffer(frame.red_image)
        )
        self.display.sleep()



def renderToFrame (frame, data):
    frame.draw_black.text((10, 0), 'Hello, world!' + data['line1'], font = font24, fill = 0)
    frame.draw_red.text((10, 30), 'Hello, world?' + data['line2'], font = font24, fill = 0)

