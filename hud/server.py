import os
import pytz
import logging
from .data import loadAll
from .data.helpers import getNow
from time import sleep

from hud import settings

class Server:
    def __init__ (self, tick_s=60, display_mode=None):
        logging.debug(f'Server init tick_s={tick_s}')
        self.tick_s = tick_s

        if settings.DEBUG_GRAPHIC:
            logging.debug(f'Server init using SVG file Renderer')
            from .renderer.svgfile import Renderer
        else:
            logging.debug(f'Server init using e-paper Renderer')
            from .renderer.epaper import Renderer
        self._renderer = Renderer()


    def tick (self):
        logging.debug(f'Server fetching')
        start_t = getNow()
        data = loadAll()
        data['now'] = start_t.astimezone(pytz.timezone(settings.DISPLAY_TZ))
        logging.debug(data['now'])

        logging.debug(f'Server displaying')
        self._renderer.render(data)
        end_t = getNow()
        work_seconds = (end_t - start_t).total_seconds()
        with open(os.path.join(os.getcwd(), '.cache/last_tick.json'),'w') as f:
            f.write(f'"{getNow().isoformat()}"')
        return work_seconds

    def start (self):
        while True:
            work_seconds = self.tick()

            sleep_seconds = int(self.tick_s - work_seconds)
            if sleep_seconds < 0:
                sleep_seconds = 10
            logging.debug(f'Server sleeping for {sleep_seconds}s')
            sleep(sleep_seconds)

