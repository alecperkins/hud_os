import logging

from .server import Server

def start ():
    Server(tick_s=60).start()

def tick ():
    Server(tick_s=60).tick()
