import pytz
from collections import defaultdict
from datetime import datetime, timezone
from hud import settings

def rDate (dt):
    color = 'black'
    if dt.day == 1:
        color = 'red'
    return f"""<g transform="translate(20,70)">
        <text class="color-{color}" style="font-size: 68px">
            {dt.strftime('%b %-d')}, {dt.strftime('%-I%p')}
        </text>
    </g>"""

def rTime (dt):
    # TODO: quarter filled circle
    return f"""<g transform="translate(20,180)">
        <text class="color-black" style="font-size: 128px;">
            
        </text>
    </g>"""

def rSunrise (sun, now):
    if not sun or not sun.get('next'):
        return ''
    hours_until = int((datetime.fromisoformat(sun['time']) - now).total_seconds() / (60 * 60))
    return f"""<g transform="translate(20,120)">
        <text class="color-black" style="font-size: 34px;">
            {sun['next'].capitalize()} in {hours_until} hours
        </text>
    </g>"""

def rAirTemp (t, h):
    color = 'black'
    if t < 33 or t > 89 or h >= 0.8:
        color = 'red'
    return f"""<g transform="translate(20,240)">
        <text class="color-{color}" style="font-size: 138px">
            {int(t)}°F {int(h*100)}%
        </text>
    </g>"""

def rFeelTemp (t):
    color = 'black'
    if t < 33 or t > 89:
        color = 'red'
    return f"""<g transform="translate(20,300)">
        <text class="color-{color}" style="font-size: 54px">
            Feels like {int(t)}°F
        </text>
    </g>"""

def rWeatherSummary (s):
    return f"""<g transform="translate(20,340)">
        <text class="color-black" style="font-size: 24px">
            {s}
        </text>
    </g>"""

def rTrainTimeList (train_times, train_statuses, now):
    lines = {
        '3': ['','black'],
        'A': ['','black'],
        'D': ['','black'],
    }
    print(1, train_times)
    train_times = sorted(train_times, key=lambda x: x['time'])
    print(2, train_times)
    for t in train_times:
        line_name = t['line']
        print(line_name, lines.get(line_name))
        if line_name in lines and not lines[line_name][0]:
            time_info = trainTimeStr(t,now)
            if time_info[0]:
                lines[line_name] = time_info
    for status in train_statuses:
        line_name = status['line']
        if line_name in lines and not lines[line_name][0]:
            lines[line_name] = [status['summary'],'red']

    # train_times = [trainTimeStr(t,now) for t in train_times]
    # train_times = list(filter(lambda x: x, train_times))
    # print(3, train_times)
    # while len(train_times) < 5:
    #     train_times.append(['','black'])
    return f"""
    <g transform="translate(20,360)">
        <g transform="translate(0,40)">
            <text class="color-{lines['3'][1]}" style="font-size: 34px">
                (3) {lines['3'][0]}
            </text>
        </g>

        <g transform="translate(0,80)">
            <text class="color-{lines['A'][1]}" style="font-size: 34px">
                (A) {lines['A'][0]}
            </text>
        </g>
    </g>
    <g transform="translate(440,360)">

        <g transform="translate(0,40)">
            <text class="color-{lines['D'][1]}" style="font-size: 24px">
                (D) {lines['D'][0]}
            </text>
        </g>

        <g transform="translate(0,60)">
        </g>

        <g transform="translate(0,80)">
        </g>

    </g>"""

def rCitiBike(station_status):
    total_available = station_status.get('num_bikes_available', 0)
    ebikes_available = station_status.get('num_ebikes_available', 0)
    station_status_str = str(total_available) + ' (E:' + str(ebikes_available) + ')'
    return f"""
    <g transform="translate(440,360)">

        <g transform="translate(0,40)">
        </g>

        <g transform="translate(0,60)">
        </g>

        <g transform="translate(0,80)">
            <text style="font-size: 24px">CitiBike: {station_status_str}</text>
        </g>

    </g>
    """

def trainTimeStr (train, now):
    stop_time = datetime.fromisoformat(train['time'])
    min_until = int((stop_time - now).total_seconds() / 60)
    print(now, stop_time, min_until)
    if min_until < 5:
        return ['','black']
    color = 'black'
    if min_until < 11:
        color = 'red'
    time_until_str = str(min_until) + 'm'
    stop_time_str = stop_time.astimezone(pytz.timezone(settings.DISPLAY_TZ)).strftime('%-H:%M')
    return [f"""in {time_until_str} at {stop_time_str}""",color]


def generateGraphic (data, color=None):
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
        ref_box = '<rect x="2" y="2" width="798" height="478" fill="none" stroke-width="1" stroke="black" />'
        color_style = """
            .color-black {
                fill: black;
            }
            .color-red {
                fill: none;
            }"""
    else:
        ref_box = '<rect x="2" y="2" width="798" height="478" fill="none" stroke-width="1" stroke="black" />'
        color_style = """
            .color-black {
                fill: black;
            }
            .color-red {
                fill: red;
            }"""
    svg_output = f"""<svg width="800" height="480" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="800" height="480" fill="white" stroke="none" />' 
    { ref_box }
    <style>
        text {{
            font-family: monospace;
        }}
        {color_style}
    </style>
    {rDate(data['now'])}
    {rTime(data['now'])}
    {rAirTemp(data['forecast']['current_temp_f'], data['forecast']['humidity'])}
    {rFeelTemp(data['forecast']['feel_temp_f'])}
    {rWeatherSummary(data['forecast']['summary'])}
    {rSunrise(data['sun'], data['now'])}
    {rTrainTimeList(data.get('subway_realtime',[]), data.get('subway_status', []), data['now'])}
    {rCitiBike(data.get('citibike'))}
</svg>
"""
    return svg_output
