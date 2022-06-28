import logging

from .controller import HUDController

def start ():
    HUDController(tick_s=60).start()

def tick ():
    HUDController(tick_s=60).tick()
