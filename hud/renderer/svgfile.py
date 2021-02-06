import os
from .graphic import generateGraphic

class Renderer:
    def __init__ (self):
        pass

    def render(self, data):
        with open(os.path.join(os.getcwd(), 'debug-graphic.svg'), 'w') as f:
            f.write(generateGraphic(data))

