import os
from PIL import Image,ImageDraw,ImageFont
from cairosvg import svg2png
import io
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
    def __init__ (self, display):
        self.display = display

    def render (self, data):
        frame = DisplayFrame(self.display.width, self.display.height)
        graphic_b = renderGraphic(data, 'black')
        graphic_r = renderGraphic(data, 'red')
        with open('./last_black.svg','w') as f:
            f.write(graphic_b)
        with open('./last_red.svg','w') as f:
            f.write(graphic_r)
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

from collections import defaultdict
from datetime import datetime, timezone
# <rect fill="#fff" stroke="#000" x="-70" y="-70" width="390" height="390"/>
# <g opacity="0.8">
# 	<rect x="25" y="25" width="200" height="200" fill="green" stroke-width="4" stroke="pink" />
# 	<circle cx="125" cy="125" r="75" fill="orange" />
# 	<polyline points="50,150 50,200 200,200 200,100" stroke="red" stroke-width="4" fill="none" />
# 	<line x1="50" y1="50" x2="200" y2="200" stroke="blue" stroke-width="4" />
# </g>


def rDate (dt):
    color = 'black'
    if dt.day == 1:
        color = 'red'
    return f"""<g transform="translate(20,70)">
        <text class="color-{color}" style="font-size: 68px">
            {dt.strftime('%b %-d')}
        </text>
    </g>"""

def rTime (dt):
    return f"""<g transform="translate(20,180)">
        <text class="color-black" style="font-size: 128px;">
            {dt.strftime('%-H:%M')}
        </text>
    </g>"""

def rAirTemp (t, h):
    color = 'black'
    if t < 33 or t > 89 or h >= 0.8:
        color = 'red'
    return f"""<g transform="translate(20,250)">
        <text class="color-{color}" style="font-size: 68px">
            {int(t)}°F {int(h*100)}%
        </text>
    </g>"""

def rFeelTemp (t):
    color = 'black'
    if t < 33 or t > 89:
        color = 'red'
    return f"""<g transform="translate(20,290)">
        <text class="color-{color}" style="font-size: 34px">
            Feels like {t}°F
        </text>
    </g>"""

def rWeatherSummary (s):
    return f"""<g transform="translate(20,330)">
        <text class="color-black" style="font-size: 34px">
            {s}
        </text>
    </g>"""

def rTrainTimeList (train_times, now):
    train_times = sorted(train_times, key=lambda x: x['time'])[0:5]
    train_times = [trainTimeStr(t,now) for t in train_times]
    train_times = list(filter(lambda x: x, train_times))
    while len(train_times) < 5:
        train_times.append(['','black'])
    return f"""
    <g transform="translate(400,20)">
        <g transform="translate(0,40)">
            <text class="color-{train_times[0][1]}" style="font-size: 34px">
                {train_times[0][0]}
            </text>
        </g>

        <g transform="translate(0,80)">
            <text class="color-{train_times[1][1]}" style="font-size: 34px">
                {train_times[1][0]}
            </text>
        </g>

        <g transform="translate(0,110)">
            <text class="color-{train_times[2][1]}" style="font-size: 24px">
                {train_times[2][0]}
            </text>
        </g>

        <g transform="translate(0,130)">
            <text class="color-{train_times[3][1]}" style="font-size: 24px">
                {train_times[3][0]}
            </text>
        </g>

        <g transform="translate(0,160)">
            <text class="color-{train_times[4][1]}" style="font-size: 24px">
                {train_times[4][0]}
            </text>
        </g>

    </g>"""

def trainTimeStr (train, now):
    stop_time = datetime.fromtimestamp(train['time']).replace(tzinfo=timezone.utc)
    stop_time.strftime('')
    min_until = int((stop_time - now).total_seconds() / 60)
    if min_until < 0:
        return []
    
    color = 'black'
    if min_until < 10:
        color = 'red'
    time_until_str = str(min_until) + 'm'
    stop_time_str = stop_time.strftime('%-H:%M')
    return [f"""({train['line']}) in {time_until_str} at {stop_time_str}""",color]

def rTrainLineStatus (statuses):
    status_by_line = defaultdict(set)
    for status in statuses:
        status_by_line[status['line']].add(status['summary'])
    return ''.join([])

def renderGraphic (data, color=None):
    if color == 'red':
        ref_box = ''
        color_style = """
            .color-black {
                fill: none;
            }
            .color-red {
                fill: black;
            }"""
    elif color == 'black':
        ref_box = '<rect x="2" y="2" width="798" height="478" fill="white" stroke-width="1" stroke="black" />'
        color_style = """
            .color-black {
                fill: black;
            }
            .color-red {
                fill: none;
            }"""
    else:
        ref_box = '<rect x="2" y="2" width="798" height="478" fill="white" stroke-width="1" stroke="black" />'
        color_style = """
            .color-black {
                fill: black;
            }
            .color-red {
                fill: red;
            }"""
    svg_output = f"""<svg width="800" height="480" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg">
    { ref_box }
    <style>
        text {{
            font-family: monospace;
        }}
        {color_style}
    </style>
    {rDate(data['now'])}
    {rTime(data['now'])}
    {rAirTemp(data['weather']['current_temp_f'], data['weather']['humidity'])}
    {rFeelTemp(data['weather']['feel_temp_f'])}
    {rWeatherSummary(data['weather']['summary'])}
    {rTrainTimeList(data['subway_realtime'], data['now'])}
    {rTrainLineStatus(data['subway_status'])}
</svg>
"""
    return svg_output
