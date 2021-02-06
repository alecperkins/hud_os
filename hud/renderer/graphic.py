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
            Feels like {int(t)}°F
        </text>
    </g>"""

def rWeatherSummary (s):
    return f"""<g transform="translate(20,330)">
        <text class="color-black" style="font-size: 14px">
            {s}
        </text>
    </g>"""

def rTrainTimeList (train_times, now):
    print(train_times)
    train_times = sorted(train_times, key=lambda x: x['time'])[0:5]
    print(train_times)
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
    stop_time = datetime.fromisoformat(train['time'])
    min_until = int((stop_time - now).total_seconds() / 60)
    print(now, stop_time, min_until)
    if min_until < 5:
        return []
    color = 'black'
    if min_until < 11:
        color = 'red'
    time_until_str = str(min_until) + 'm'
    stop_time_str = stop_time.astimezone(pytz.timezone(settings.DISPLAY_TZ)).strftime('%-H:%M')
    return [f"""({train['line']}) in {time_until_str} at {stop_time_str}""",color]

def rTrainLineStatus (statuses):
    status_by_line = defaultdict(set)
    for status in statuses:
        status_by_line[status['line']].add(status['summary'])
    return ''.join([])

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
    {rTrainTimeList(data['subway_realtime'], data['now'])}
    {rTrainLineStatus(data['subway_status'])}
</svg>
"""
    return svg_output
