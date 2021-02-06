import logging

def start():
    from .server import Server
    Server(tick_s=60).start()

